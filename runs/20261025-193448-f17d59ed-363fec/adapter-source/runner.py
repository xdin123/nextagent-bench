from __future__ import annotations

import concurrent.futures
import contextlib
import json
import os
import threading
import time
import uuid
import shutil
from pathlib import Path

from .artifacts import framework_image
from .docker import Container, ensure_task_image
from .paths import adapt_task, make_mappings
from .results import event_metrics, resume_identity, summarize_verifier
from .settings import HOME, load_task
from .gateway import ModelGateway, credential_ring
from .util import adapter_sha, command, digest, now, read_json, sanitize, tree_manifest, write_json, archive_from_container

TERMINALS = {"REQUEST_COMPLETED", "REQUEST_FAILED", "GUARD_BLOCKED", "REQUEST_BLOCKED", "REQUEST_CANCELLED", "REQUEST_CANCELED"}
INVALID = {"ENVIRONMENT_ERROR", "PREFLIGHT_ERROR", "HARNESS_ERROR", "VERIFIER_ERROR", "INTERRUPTED"}


def terminal_event(events: list[dict]) -> dict | None:
    return next((event for event in reversed(events) if event.get("eventType") in TERMINALS or (event.get("payload") or {}).get("guardBlocked") is True), None)


def poll_run(container: Container, session: str, run: str, request: str, timeout: float,
             trajectory: Path, stop_requested=lambda: False, after_sequence: int = 0) -> dict:
    deadline = time.monotonic() + timeout
    sequence, seen, terminal = after_sequence, set(), None
    trajectory.parent.mkdir(parents=True, exist_ok=True)
    errors = 0
    with trajectory.open("a", encoding="utf-8") as stream:
        while time.monotonic() < deadline:
            if stop_requested():
                return {"status": "INTERRUPTED", "payload": {}, "last_sequence": sequence}
            try:
                page = container.rpc("GET", f"/api/v1/sessions/{session}/runs/{run}/events?afterSequence={sequence}&limit=1000")
                events = page.get("events")
                if not isinstance(events, list):
                    raise ValueError("Invalid run event page: events must be an array")
                errors = 0
            except Exception:
                errors += 1
                if errors >= 5:
                    raise
                time.sleep(1)
                continue
            for event in events:
                event_id = event.get("eventId")
                event_sequence = event.get("sequence")
                if not isinstance(event_id, str) or not isinstance(event_sequence, int):
                    raise ValueError("Invalid event identity/sequence")
                if event_sequence <= after_sequence:
                    continue
                sequence = max(sequence, event_sequence)
                if event_id not in seen:
                    seen.add(event_id)
                    stream.write(json.dumps(event, ensure_ascii=False) + "\n")
            stream.flush()
            terminal = terminal_event(events)
            if terminal:
                return {"status": terminal["eventType"], "payload": terminal.get("payload", {}), "sequence": terminal["sequence"]}
            if len(events) >= 1000:
                continue
            time.sleep(min(1.5, max(0, deadline - time.monotonic())))
    return {"status": "TIMEOUT", "payload": {}, "last_sequence": sequence}


def submit(container: Container, prompt: str) -> dict:
    session = container.rpc("POST", "/api/v1/sessions", {"locale": "zh-CN"})["sessionId"]
    accepted = container.rpc("POST", f"/api/v1/sessions/{session}/requests", {
        "inputText": prompt, "idempotencyKey": "bench-" + uuid.uuid4().hex, "locale": "zh-CN",
        "routingConstraints": {"allowHumanInput": False},
    })
    return {"sessionId": session, "runId": accepted["runId"], "requestId": accepted["requestId"]}


class MemoryGate:
    def __init__(self, capacity: int):
        self.capacity, self.used = capacity, 0
        self.condition = threading.Condition()

    @contextlib.contextmanager
    def reserve(self, amount: int):
        if amount > self.capacity:
            raise ValueError(f"Task declares {amount} MiB; evaluation memory budget is {self.capacity} MiB")
        with self.condition:
            self.condition.wait_for(lambda: self.used + amount <= self.capacity)
            self.used += amount
        try:
            yield
        finally:
            with self.condition:
                self.used -= amount
                self.condition.notify_all()


def create_run(project: Path, config: dict, artifact: dict, dataset: dict, tasks: list[str], jobs: int) -> Path:
    identifier = time.strftime("%Y%m%d-%H%M%S") + "-" + artifact["sha256"][:8] + "-" + uuid.uuid4().hex[:6]
    directory = project / "runs" / identifier
    directory.mkdir(parents=True)
    manifest = {"run_id": identifier, "created_at": now(), "framework_sha": artifact["sha256"],
                "dataset_sha": dataset["sha256"], "profile_sha": config["profile_sha"], "adapter_sha": adapter_sha(),
                "model": config["model"], "base_url": config["base_url"], "tasks": tasks,
                "requested_jobs": jobs, "jobs": min(jobs, config["quota"]["max_concurrency"]), "quota": config["quota"],
                "model_transport": "private-shared-quota-gateway",
                "analysis": config["analysis"],
                "skill_mode": config.get("skill_mode", "with-skill"), "framework": artifact,
                "dataset": dataset, "status": "CREATED", "legacy_environment_images": config.get("legacy_environment_images", {})}
    manifest["resume_identity"] = resume_identity(manifest)
    write_json(directory / "manifest.json", manifest)
    source = Path(__file__).parent
    for path in source.rglob("*"):
        if path.is_file() and path.suffix in {".py", ".mjs"} and "__pycache__" not in path.parts:
            target = directory / "adapter-source" / path.relative_to(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
    for name, value in (("default-system.yaml", config["effective_system"]), ("agent.yaml", config["effective_agent"]),
                        ("changes.json", config["config_changes"]), ("path-policy.json", config.get("path_policy", {})),
                        ("quota.json", config["quota"])):
        write_json(directory / "config" / name, value)
    return directory


def check_resume(directory: Path) -> dict:
    manifest = read_json(directory / "manifest.json")
    if manifest.get("adapter_sha") != adapter_sha():
        raise ValueError("Adapter changed since this run. Start a new batch; old results remain intact.")
    if manifest.get("resume_identity") != resume_identity(manifest):
        raise ValueError("Run identity changed; refusing to mix results")
    snapshot = {"system": read_json(directory / "config" / "default-system.yaml"),
                "agent": read_json(directory / "config" / "agent.yaml"),
                "changes": json.loads((directory / "config" / "changes.json").read_text(encoding="utf-8")),
                "path_policy": read_json(directory / "config" / "path-policy.json"),
                "quota": read_json(directory / "config" / "quota.json")}
    if digest(snapshot) != manifest.get("profile_sha"):
        raise ValueError("Frozen configuration/path mapping changed; start a new batch")
    return manifest


def execute_task(project: Path, run_dir: Path, manifest: dict, task_id: str, image: str,
                 build_gate: threading.Semaphore, memory: MemoryGate, gateway: ModelGateway, keep: bool = False) -> dict:
    if (run_dir / "STOP").exists():
        return {"task": task_id, "outcome": "PENDING"}
    task = project / "datasets" / manifest["dataset_sha"] / "tasks" / task_id
    budget = load_task(task)
    task_dir = run_dir / "tasks" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    number = max([int(path.name.split("-")[-1]) for path in task_dir.glob("attempt-*") if path.is_dir()] or [0]) + 1
    attempt = task_dir / f"attempt-{number:03d}"
    attempt.mkdir()
    result = {"task": task_id, "attempt": number, "run_id": manifest["run_id"], "model": manifest["model"],
              "framework_sha": manifest["framework_sha"], "started_at": now(), "phase": "queued", "status": "RUNNING",
              "budgets": budget, "score": None, "reward": None, "phase_seconds": {}, "artifact_errors": []}
    start, phase_start = time.monotonic(), time.monotonic()
    container = Container("nab-" + manifest["run_id"].replace("_", "-") + "-" + task_id[:35] + f"-{number}",
                          "nab-" + uuid.uuid4().hex[:12], task, budget, attempt)
    outcome = None

    def persist():
        result["elapsed_seconds"] = round(time.monotonic() - start, 3)
        write_json(attempt / "result.json", result)

    def phase(name):
        nonlocal phase_start
        elapsed = time.monotonic()
        result["phase_seconds"][result["phase"]] = round(elapsed - phase_start, 3)
        phase_start = elapsed
        result["phase"] = name
        persist()

    try:
        persist()
        expected = read_json(project / "datasets" / manifest["dataset_sha"] / "files.json")
        prefix = task_id + "/"
        expected = {name[len(prefix):]: value for name, value in expected.items() if name.startswith(prefix)}
        if expected != tree_manifest(task):
            raise ValueError("Frozen task snapshot changed; import a new dataset")
        with memory.reserve(budget["memory_mb"]):
            if (run_dir / "STOP").exists():
                result["outcome"] = "INTERRUPTED"
                return result
            phase("build")
            with build_gate:
                task_image, image_metadata = ensure_task_image(project, task, image, manifest["framework"]["candidate"].get("nodeVersion", "v22.22.0"),
                                                               budget, attempt, manifest.get("legacy_environment_images", {}).get(task_id))
            if (run_dir / "STOP").exists():
                raise InterruptedError("Stop requested after build")
            result["environment"] = image_metadata
            policy = read_json(run_dir / "config" / "path-policy.json")
            mappings = make_mappings(image_metadata["workdir"], policy.get(task_id, {}).get("extra_roots", []))
            audit = adapt_task(task, attempt / "agent-facing", mappings)
            result["provided_skills"] = audit["provided_skills"]
            phase("container_setup")
            with build_gate:
                container.start(task_image, manifest["run_id"])
                gateway.connect(container.name)
            result["container"] = container.name
            write_json(attempt / "container-inspect.json", json.loads(command(["docker", "inspect", "--format", "{{json .HostConfig}}", container.name]).stdout))
            definition = read_json(run_dir / "config" / "agent.yaml")
            container.helper("prepare", {"agentId": definition["agentId"]})
            container.put(run_dir / "config" / "default-system.yaml", "/opt/nextagent/config/evaluation-system.yaml")
            container.put(run_dir / "config" / "agent.yaml", HOME + "/agents/" + definition["agentId"] + "/agent.yaml")
            container.put(attempt / "agent-facing", "/opt/na-eval/run/agent-facing")
            if manifest["skill_mode"] == "with-skill" and (attempt / "agent-facing" / "skills").exists():
                container.put(str(attempt / "agent-facing" / "skills") + "/.", HOME + "/skills/")
            phase("bootstrap")
            task_url = gateway.task_url(task_id, number)
            write_json(attempt / "model-transport.json", {"model": manifest["model"], "internal_url": task_url,
                       "upstream": manifest["base_url"], "credential": "temporary gateway token; upstream keys stay in the sidecar"})
            container.launch(manifest["model"], task_url, gateway.token)
            deadline = time.monotonic() + 150
            while True:
                if (run_dir / "STOP").exists():
                    raise InterruptedError("Stop requested")
                try:
                    bootstrap = container.rpc("GET", "/api/v1/runtime/bootstrap")
                    break
                except Exception:
                    if not container.helper("status").get("running"):
                        logs = container.helper("read", {"paths": ["/opt/na-eval/run/na-start.log"]})
                        raise RuntimeError("NextAgent process exited during bootstrap: " + (logs.get("/opt/na-eval/run/na-start.log") or "no startup log")[-3000:])
                    if time.monotonic() >= deadline:
                        raise TimeoutError("NextAgent bootstrap did not become ready")
                    time.sleep(2)
            write_json(attempt / "bootstrap.json", bootstrap)
            expected_guard = definition.get("runtimeSettings", {}).get("guardrailEnabled")
            if isinstance(expected_guard, bool) and bootstrap.get("guardrail", {}).get("enabled") != expected_guard:
                raise ValueError("Effective guardrail configuration differs from the frozen agent template")
            phase("skill_preflight")
            discovered, pages = set(), []
            page_number = 1
            while True:
                page = container.rpc("GET", f"/api/v1/skills?pageNum={page_number}&pageSize=100")
                pages.append(page)
                discovered.update(item["capabilityId"] for item in page.get("skills", []))
                if page_number * 100 >= page.get("total", 0):
                    break
                page_number += 1
            write_json(attempt / "skill-catalog.json", pages)
            # Web lists only user-invocable Skills. Standard benchmark Skills
            # may be model-invocable without being user-invocable; registered
            # system-local diagnostics prove they entered discovery at startup.
            discovery = container.helper("skill-discovery")
            write_json(attempt / "skill-discovery.json", discovery)
            discovered.update(discovery["registered"])
            expected = {item["name"] for item in audit["provided_skills"]} if manifest["skill_mode"] == "with-skill" else set()
            result["skills_discoverable"] = sorted(discovered)
            if expected - discovered:
                raise ValueError("Task Skills not discoverable: " + ", ".join(sorted(expected - discovered)))
            phase("workspace_preflight")
            prime = submit(container, "Run exactly this Bash command and report its output: echo __nextagent_bench_ready__. Do not use other tools.")
            write_json(attempt / "priming.json", prime)
            primed = poll_run(container, prime["sessionId"], prime["runId"], prime["requestId"], 120, attempt / "priming-trajectory.jsonl",
                              lambda: (run_dir / "STOP").exists())
            if primed["status"] != "REQUEST_COMPLETED":
                raise ValueError("Framework tool preflight failed: " + json.dumps(primed, ensure_ascii=False))
            bridge = container.helper("bridge", {"mappings": mappings}, timeout=300)
            result["workspace"] = bridge["workspace"]
            write_json(attempt / "path-bridge.json", bridge)
            phase("agent")
            accepted = submit(container, (attempt / "agent-facing" / "prompt.txt").read_text(encoding="utf-8"))
            result.update(accepted)
            result["accepted_at"] = now()
            persist()
            outcome = poll_run(container, accepted["sessionId"], accepted["runId"], accepted["requestId"], budget["agent_timeout"],
                               attempt / "trajectory.jsonl", lambda: (run_dir / "STOP").exists())
            result["terminal"] = outcome
            result["terminal_at"] = now()
            if outcome["status"] in {"TIMEOUT", "INTERRUPTED"}:
                phase("cancel")
                try:
                    result["cancellation"] = container.rpc("POST", f"/api/v1/sessions/{accepted['sessionId']}/cancel", {
                        "expectedLatestRequestId": accepted["requestId"], "idempotencyKey": "cancel-" + uuid.uuid4().hex, "action": "CANCEL"})
                    result["cancellation_terminal"] = poll_run(container, accepted["sessionId"], accepted["runId"], accepted["requestId"],
                                                               15, attempt / "trajectory.jsonl", after_sequence=outcome.get("last_sequence", 0))
                except Exception as error:
                    result["cancellation_error"] = sanitize(str(error))
            phase("stop_application")
            result["application_stop"] = container.stop_application()
            phase("verifier")
            container.put(task / "verifier", "/verifier")
            verification = container.exec(["sh", "-c", "mkdir -p /logs/verifier && echo $$ > /opt/na-eval/run/verifier.pid && exec bash /verifier/test.sh"],
                                          timeout=budget["verifier_timeout"], check=False, log=attempt / "verifier-stdout.txt")
            texts = container.helper("read", {"paths": ["/logs/verifier/reward.txt", "/logs/verifier/ctrf.json"]})
            ctrf = json.loads(texts.get("/logs/verifier/ctrf.json") or "{}")
            write_json(attempt / "ctrf.json", ctrf)
            (attempt / "reward.txt").write_text(texts.get("/logs/verifier/reward.txt") or "", encoding="utf-8")
            verified = summarize_verifier(texts.get("/logs/verifier/reward.txt") or "", ctrf, verification.returncode)
            result.update({"verifier": verified, "reward": verified["reward"]})
            if outcome["status"] == "REQUEST_COMPLETED":
                result["outcome"] = verified["outcome"]
                result["score"] = verified["reward"]
            elif outcome["status"] in {"TIMEOUT", "INTERRUPTED"}:
                result["outcome"] = outcome["status"]
                result["score"] = 0 if outcome["status"] == "TIMEOUT" else None
            else:
                result["outcome"] = "EXECUTION_FAILED"
                result["score"] = 0
            payload = outcome.get("payload") or {}
            (attempt / "final-answer.txt").write_text(str(payload.get("content") or payload.get("text") or ""), encoding="utf-8")
    except Exception as error:
        phase_name = result["phase"]
        result["failed_phase"] = phase_name
        result["error"] = sanitize(str(error))
        result["outcome"] = ("INTERRUPTED" if isinstance(error, (InterruptedError, KeyboardInterrupt)) else
                             "ENVIRONMENT_ERROR" if phase_name in {"queued", "build", "container_setup"} else
                             "PREFLIGHT_ERROR" if phase_name in {"bootstrap", "skill_preflight", "workspace_preflight"} else
                             "VERIFIER_ERROR" if phase_name == "verifier" else "HARNESS_ERROR")
        if result["outcome"] == "PREFLIGHT_ERROR" and phase_name in {"bootstrap", "workspace_preflight"}:
            write_json(run_dir / "HALT.json", {"task": task_id, "phase": phase_name, "reason": result["error"], "at": now()})
            (run_dir / "STOP").write_text("Common framework/tool preflight failed; inspect HALT.json before resuming.\n", encoding="utf-8")
    finally:
        phase("collect")
        if container.created:
            try:
                container.stop_application()
            except Exception:
                pass
            try:
                container.helper("stop", {"kind": "verifier"}, timeout=60)
            except Exception as error:
                result["artifact_errors"].append("Could not confirm verifier stopped: " + sanitize(str(error)))
            try:
                result["home_archive"] = container.archive_home(attempt / "nextagent-home.tar")
            except Exception as error:
                result["artifact_errors"].append(sanitize(str(error)))
            for source, target, required in (("/opt/na-eval/run", "runtime", True),
                                              ("/logs", "verifier-logs", False), ("/opt/nextagent/run", "deployment-run", False)):
                try:
                    if not container.get(source, attempt / target, required=required) and required:
                        result["artifact_errors"].append(source)
                except Exception as error:
                    result["artifact_errors"].append(sanitize(str(error)))
            if not keep:
                container.close()
        trajectory = attempt / "trajectory.jsonl"
        if trajectory.exists():
            events = [json.loads(line) for line in trajectory.read_text(encoding="utf-8").splitlines() if line.strip()]
            result.update(event_metrics(events))
        phase("finished")
        result["status"], result["finished_at"] = "FINISHED", now()
        if result["artifact_errors"]:
            result["evidence_complete"] = False
        else:
            result["evidence_complete"] = container.created
        persist()
        write_json(attempt / "phase-timing.json", result["phase_seconds"])
        print(f"{task_id} attempt={number} outcome={result.get('outcome')} score={result.get('score')} seconds={result['elapsed_seconds']}", flush=True)
    return result


def recover_containers(directory: Path) -> dict:
    """Only after the owning runner stopped: archive and remove its orphans."""
    manifest = read_json(directory / "manifest.json")
    identifiers = command(["docker", "ps", "-aq", "--filter", "label=nextagent-bench.run=" + manifest["run_id"]]).stdout.split()
    destination = directory / "recovery" / time.strftime("%Y%m%d-%H%M%S")
    records = []
    for identifier in identifiers:
        label = command(["docker", "inspect", "--format", '{{index .Config.Labels "nextagent-bench.run"}}', identifier]).stdout.strip()
        if label != manifest["run_id"]:
            raise ValueError("Recovery refused a container outside this batch")
        target = destination / identifier
        target.mkdir(parents=True, exist_ok=True)
        container = Container(identifier, "", Path("."), {}, target)
        record = {"container": identifier, "errors": []}
        role = command(["docker", "inspect", "--format", '{{index .Config.Labels "nextagent-bench.role"}}', identifier]).stdout.strip()
        if role == "model-gateway":
            try:
                archive_from_container(identifier, "/evidence", target / "exchanges.tar")
                logs = command(["docker", "logs", identifier], check=False)
                (target / "events.jsonl").write_text(logs.stdout, encoding="utf-8")
            except Exception as error:
                record["errors"].append(sanitize(str(error)))
            command(["docker", "rm", "-f", identifier], timeout=60, check=False)
            records.append(record)
            continue
        try:
            container.stop_application()
        except Exception as error:
            record["errors"].append("Application stop: " + sanitize(str(error)))
        try:
            record["archive"] = container.archive_home(target / "nextagent-home.tar")
            container.get("/opt/na-eval/run", target / "runtime", required=False)
        except Exception as error:
            record["errors"].append(sanitize(str(error)))
        command(["docker", "rm", "-f", identifier], timeout=60, check=False)
        records.append(record)
    for path in directory.glob("tasks/*/attempt-*/compose-owner.json"):
        owner = read_json(path)
        project = owner.get("project", "")
        if not project.startswith("nab-"):
            raise ValueError("Invalid owned Compose project")
        command(["docker", "compose", "--project-directory", owner["directory"], "-p", project, "-f", str(path.parent / "compose.effective.yaml"),
                 "down", "--volumes", "--remove-orphans"], timeout=120, check=False)
    for path in directory.glob("tasks/*/attempt-*/result.json"):
        result = read_json(path)
        if result.get("status") != "FINISHED":
            result.update({"status": "FINISHED", "outcome": "INTERRUPTED", "finished_at": now(), "recovery": str(destination), "score": None})
            write_json(path, result)
    networks = command(["docker", "network", "ls", "-q", "--filter", "label=nextagent-bench.run=" + manifest["run_id"]]).stdout.split()
    for network in networks:
        command(["docker", "network", "rm", network], check=False)
    summary = {"at": now(), "containers": records}
    write_json(destination / "recovery.json", summary)
    return summary


def run_batch(project: Path, directory: Path, *, retry_errors: bool = False, keep: bool = False) -> None:
    manifest = check_resume(directory)
    credential_ring()
    gateway = ModelGateway(project, directory, manifest)
    lock = directory / "runner.lock"
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise ValueError(f"Run is already owned by a runner. Inspect {lock}; use resume --recover only after that process has stopped.")
    os.write(descriptor, str(os.getpid()).encode())
    os.close(descriptor)
    try:
        (directory / "STOP").unlink(missing_ok=True)
        (directory / "HALT.json").unlink(missing_ok=True)
        manifest["status"], manifest["runner_pid"] = "RUNNING", os.getpid()
        write_json(directory / "manifest.json", manifest)
        image = framework_image(project, manifest["framework"], directory / "framework-build.log")
        gateway.start()
        memory_total = int(command(["docker", "info", "--format", "{{.MemTotal}}"]).stdout.strip()) // (1024 * 1024)
        memory = MemoryGate(int(memory_total * 0.80))
        build_gate = threading.Semaphore(1)
        pending = []
        for task in manifest["tasks"]:
            results = sorted((directory / "tasks" / task).glob("attempt-*/result.json"))
            latest = read_json(results[-1]) if results else None
            if latest and latest.get("status") == "FINISHED" and latest.get("outcome") != "INTERRUPTED" and not (retry_errors and latest.get("outcome") in INVALID):
                continue
            pending.append(task)
        with concurrent.futures.ThreadPoolExecutor(max_workers=manifest["jobs"]) as pool:
            futures = [pool.submit(execute_task, project, directory, manifest, task, image, build_gate, memory, gateway, keep) for task in pending]
            try:
                for future in concurrent.futures.as_completed(futures):
                    future.result()
            except KeyboardInterrupt:
                (directory / "STOP").write_text("Interrupted by operator\n", encoding="utf-8")
                for future in futures:
                    future.cancel()
                raise
        manifest["status"] = "HALTED" if (directory / "HALT.json").exists() else "STOPPED" if (directory / "STOP").exists() else "FINISHED"
        manifest["finished_at"] = now()
        write_json(directory / "manifest.json", manifest)
        if manifest.get("analysis", {}).get("enabled", True):
            from .analysis import analyze_failures
            try:
                gateway.export_evidence()
                analyze_failures(project, directory, gateway, manifest["analysis"])
            except Exception as error:
                write_json(directory / "analysis-error.json", {"error": sanitize(str(error)), "at": now(),
                           "note": "Task results are unchanged. Diagnostics can be rerun independently."})
    except BaseException as error:
        manifest["status"], manifest["runner_error"] = "STOPPED" if isinstance(error, KeyboardInterrupt) else "ERROR", sanitize(str(error))
        write_json(directory / "manifest.json", manifest)
        raise
    finally:
        try:
            gateway.close()
        except Exception as error:
            write_json(directory / "model-gateway-close-error.json", {"error": sanitize(str(error)), "at": now()})
        lock.unlink(missing_ok=True)
        from .report import generate_report
        try:
            generate_report(directory)
        except Exception as error:
            write_json(directory / "report-error.json", {"error": sanitize(str(error)), "at": now()})
            print("Report generation failed; task evidence remains saved: " + sanitize(str(error)), file=__import__('sys').stderr)
