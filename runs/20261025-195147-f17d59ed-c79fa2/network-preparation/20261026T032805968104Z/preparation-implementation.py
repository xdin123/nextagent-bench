"""Prepare exact network-retry environments, then resume the original batch."""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import threading
import uuid
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))

from nextagent_bench.artifacts import framework_image
from nextagent_bench.concurrency import request_task_retries
from nextagent_bench.docker import NODE, ensure_task_image
from nextagent_bench.gateway import ModelGateway
from nextagent_bench.runner import MemoryGate, check_resume, run_batch
from nextagent_bench.settings import load_task
from nextagent_bench.util import command, now, read_json, sanitize, tree_manifest, write_json


def worker(run: Path, task_id: str, framework: str, output: Path):
    manifest = check_resume(run)
    task = PROJECT / "datasets" / manifest["dataset_sha"] / "tasks" / task_id
    expected = read_json(PROJECT / "datasets" / manifest["dataset_sha"] / "files.json")
    prefix = task_id + "/"
    if {k[len(prefix):]: v for k, v in expected.items() if k.startswith(prefix)} != tree_manifest(task):
        raise ValueError("Frozen task changed: " + task_id)
    budget = load_task(task)
    original_timeout = budget["build_timeout"]
    # This is separate cache preparation. The scored attempt keeps its frozen budget.
    budget["build_timeout"] = max(original_timeout, 7200)
    image, metadata = ensure_task_image(PROJECT, task, framework,
        manifest["framework"]["candidate"].get("nodeVersion", "v22.22.0"), budget, output,
        manifest.get("legacy_environment_images", {}).get(task_id))
    command(["docker", "run", "--rm", "--name", "nab-ready-" + uuid.uuid4().hex[:12],
             "--label", "nextagent-bench.run=" + manifest["run_id"],
             "--label", "nextagent-bench.role=readiness-check", "--memory", str(budget["memory_mb"]) + "m",
             "--cpus", str(budget["cpus"]), "--entrypoint", NODE, image, "--version"], timeout=60,
            log=output / "readiness.log")
    write_json(output / "ready.json", {"task": task_id, "at": now(), "image": image,
        "image_metadata": metadata, "original_build_timeout_seconds": original_timeout,
        "scored_budget_unchanged": True})


def validate_model(run: Path, manifest: dict, output: Path):
    gateway = ModelGateway(PROJECT, run, manifest)
    result = {"at": now(), "model": manifest["model"], "maximum_output_tokens": 8}
    try:
        gateway.start()
        response = gateway.completion("__network_probe", 1,
            {"model": manifest["model"], "stream": True, "temperature": 0, "max_tokens": 8,
             "messages": [{"role": "user", "content": "Reply OK."}]}, 45)
        metrics = gateway.metrics()
        result.update({"statuses": metrics["statuses"], "passed": bool(metrics["statuses"].get("200")) and not response.get("error")})
        write_json(output / "model-validation.json", result)
        if not result["passed"]:
            raise ValueError("Authenticated Docker model validation failed; no evaluation started")
    finally:
        gateway.close()


def main(run: Path):
    manifest = check_resume(run)
    plan = read_json(run / "network-retry-plan.json")
    if plan["run_id"] != manifest["run_id"] or (run / "runner.lock").exists():
        raise ValueError("Invalid recovery plan or active runner")
    for name, expected in plan["first_pass_result_hashes"].items():
        if hashlib.sha256((run / name).read_bytes()).hexdigest() != expected:
            raise ValueError("Original result changed before network recovery: " + name)
    lock = run / "network-recovery.lock"
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(descriptor, str(os.getpid()).encode())
    os.close(descriptor)
    output = run / "network-preparation" / datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output.mkdir(parents=True)
    shutil.copyfile(Path(__file__), output / "preparation-implementation.py")
    state = {"run_id": manifest["run_id"], "pid": os.getpid(), "phase": "PREPARING", "started_at": now(),
             "directory": str(output), "selected_count": len(plan["selected"]), "ready_count": 0, "failed_count": 0, "tasks": {}}
    guard = threading.Lock()
    stop_path = run / "STOP"
    original_stop_stamp = stop_path.stat().st_mtime_ns if stop_path.exists() else None

    def operator_stopped():
        return (run / "DRAIN").exists() or (stop_path.exists() and stop_path.stat().st_mtime_ns != original_stop_stamp)

    def publish():
        write_json(run / "network-recovery-state.json", state)

    def prepare(item: dict, framework: str, memory: MemoryGate):
        task_id = item["task"]
        budget = load_task(PROJECT / "datasets" / manifest["dataset_sha"] / "tasks" / task_id)
        destination = output / task_id
        destination.mkdir()
        with guard:
            state["tasks"][task_id] = {"phase": "WAITING_FOR_DECLARED_MEMORY", "memory_mb": budget["memory_mb"]}
            publish()
        try:
            with memory.reserve(budget["memory_mb"]):
                if operator_stopped():
                    with guard:
                        state["tasks"][task_id]["phase"] = "DEFERRED_BY_OPERATOR"
                        publish()
                    return None
                with guard:
                    state["tasks"][task_id].update({"phase": "PREBUILDING", "started_at": now()})
                    publish()
                child_env = {k: v for k, v in os.environ.items() if k not in {"NAB_API_KEYS", "OPENAI_API_KEY"}}
                with (destination / "worker.log").open("w", encoding="utf-8") as log:
                    process = subprocess.Popen([sys.executable, str(Path(__file__)), str(run), "--worker", task_id,
                        "--framework", framework, "--output", str(destination)], stdout=log, stderr=subprocess.STDOUT,
                        env=child_env, start_new_session=os.name != "nt")
                    try:
                        code = process.wait(timeout=plan["preparation_timeout_seconds"])
                    except subprocess.TimeoutExpired:
                        # Kill the still-owned Python worker and its Docker plugin descendants together.
                        if os.name == "nt":
                            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        else:
                            os.killpg(process.pid, signal.SIGKILL)
                        if process.poll() is None:
                            process.kill()
                        process.wait()
                        raise TimeoutError("Cache preparation exceeded its separate timeout")
                if code or not (destination / "ready.json").exists():
                    raise ValueError("Preparation failed; inspect " + str(destination / "worker.log"))
            with guard:
                state["tasks"][task_id].update({"phase": "READY", "finished_at": now(), "evidence": str(destination / "ready.json")})
                state["ready_count"] += 1
                publish()
            return task_id
        except Exception as error:
            with guard:
                state["tasks"][task_id].update({"phase": "PREPARATION_FAILED", "finished_at": now(), "error": sanitize(str(error))[:1000]})
                state["failed_count"] += 1
                publish()
            return None

    try:
        publish()
        framework = framework_image(PROJECT, manifest["framework"], output / "framework-build.log")
        memory_total = int(command(["docker", "info", "--format", "{{.MemTotal}}"]).stdout.strip()) // (1024 * 1024)
        memory = MemoryGate(int(memory_total * 0.80))
        with concurrent.futures.ThreadPoolExecutor(max_workers=plan["preparation_jobs"]) as pool:
            futures = [pool.submit(prepare, item, framework, memory) for item in plan["selected"]]
            ready = [name for future in futures if (name := future.result())]
        if operator_stopped():
            state["phase"] = "PREPARED_WAITING_FOR_OPERATOR"
            publish()
            return
        state["phase"] = "VALIDATING_MODEL"
        publish()
        validate_model(run, manifest, output)
        if ready:
            request_task_retries(run, ready, "User-authorized verified network recovery; one completed retest, original scores preserved")
        for name in ["manifest.json", "HALT.json", "STOP", "concurrency.json", "adapter-upgrade.json"]:
            if (run / name).exists():
                shutil.copyfile(run / name, output / ("before-resume-" + name))
        state.update({"phase": "EVALUATING", "evaluation_started_at": now(), "retry_tasks": ready,
                      "deferred_preparation_failures": [k for k, v in state["tasks"].items() if v["phase"] == "PREPARATION_FAILED"]})
        publish()
        observations = read_json(run / "ramp-observations.json")
        previous_scored = set()
        for result_file in run.glob("tasks/*/attempt-*/result.json"):
            value = read_json(result_file)
            if isinstance(value.get("score"), (int, float)) and not isinstance(value.get("score"), bool):
                previous_scored.add(value["task"])
        observations.update({"at": now(), "current_jobs": read_json(run / "concurrency.json")["jobs"],
                             "level_started_at": now(), "gateway_epoch_started_at": now(),
                             "baseline_completed_tasks": sorted(previous_scored), "baseline_model_metrics": {"statuses": {}, "credentials": []},
                             "stability_window_started_at": now(), "baseline_pending_gateway_start": True})
        observations["observations"].append({"at": now(), "jobs": observations["current_jobs"],
            "decision": "NETWORK_RECOVERY_NEW_GATEWAY", "metrics": {"statuses": {}, "credentials": []},
            "proxy_error_kinds": {}, "quota_wait_errors": 0,
            "reason": "Reset counters before a new gateway; precise network retries plus default pending tasks, old attempts preserved."})
        write_json(run / "ramp-observations.json", observations)
        run_batch(PROJECT, run)
        state.update({"phase": read_json(run / "manifest.json")["status"], "finished_at": now()})
        publish()
    except Exception as error:
        state.update({"phase": "BLOCKED", "error": sanitize(str(error))[:1200], "finished_at": now()})
        publish()
        raise
    finally:
        lock.unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("--worker")
    parser.add_argument("--framework")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.worker:
        worker(args.run.resolve(), args.worker, args.framework, args.output)
    else:
        main(args.run.resolve())
