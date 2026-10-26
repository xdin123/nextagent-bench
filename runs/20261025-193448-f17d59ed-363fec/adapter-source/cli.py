from __future__ import annotations

import argparse
import json
import os
import sys
import yaml
from pathlib import Path

from .artifacts import import_dataset, import_framework
from .report import generate_report
from .paths import adapt_task, make_mappings, predict_workdir
from .runner import create_run, run_batch, recover_containers, check_resume
from .settings import load_settings, load_task
from .util import command, read_document, read_json, sanitize, write_json

PROJECT = Path(__file__).resolve().parent.parent


def resolve_path(value: str) -> Path:
    path = Path(value).expanduser()
    return path.resolve() if path.is_absolute() else (PROJECT / path).resolve()


def resources(config: dict, framework: str | None, dataset: str | None) -> tuple[dict, dict]:
    artifact_path = resolve_path(framework or config["framework"])
    if (artifact_path / "bundle.tar.gz").exists() and (artifact_path / "manifest.json").exists():
        artifact = read_json(artifact_path / "manifest.json")
    else:
        artifact = import_framework(PROJECT, artifact_path)
    dataset_path = resolve_path(dataset or config["dataset"])
    if (dataset_path / "manifest.json").exists() and (dataset_path / "files.json").exists():
        data = read_json(dataset_path / "manifest.json")
    else:
        data = import_dataset(PROJECT, dataset_path)
    return artifact, data


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="NextAgent versioned Docker SkillsBench evaluation")
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ("prepare", "run", "plan"):
        child = sub.add_parser(action)
        child.add_argument("--framework", help="New Linux x64 tar.gz or explicit deployment directory")
        child.add_argument("--dataset", help="Existing SkillsBench root; imported once as a frozen snapshot")
        child.add_argument("--suite", default="full")
        child.add_argument("--tasks", nargs="+")
        child.add_argument("--jobs", type=int)
        child.add_argument("--keep-containers", action="store_true")
        if action == "prepare":
            child.add_argument("--pin-defaults", action="store_true")
    doctor = sub.add_parser("doctor")
    doctor.add_argument("--offline", action="store_true")
    for action in ("resume", "report", "status", "stop", "analyze"):
        child = sub.add_parser(action)
        child.add_argument("run", nargs="?")
        if action == "resume":
            child.add_argument("--retry-errors", action="store_true")
            child.add_argument("--recover", action="store_true")
        if action == "analyze":
            child.add_argument("--evidence-only", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.action in {"prepare", "run", "plan", "doctor"}:
            config = load_settings(PROJECT)
            config["path_policy"] = read_document(PROJECT / "profiles" / "path-mappings.yaml")
        if args.action == "doctor":
            result = {"python": sys.version.split()[0], "project": str(PROJECT), "model": config["model"],
                      "credential_present": bool(os.environ.get("OPENAI_API_KEY") or os.environ.get("NAB_API_KEYS")),
                      "shared_quota": config["quota"], "config_changes": config["config_changes"]}
            if not args.offline:
                result["docker"] = command(["docker", "info", "--format", "{{json .}}"], timeout=30).returncode == 0
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if args.action in {"prepare", "run", "plan"}:
            artifact, dataset = resources(config, args.framework, args.dataset)
            tasks = args.tasks or config.get("suites", {}).get(args.suite)
            if tasks is None:
                if args.suite != "full":
                    raise ValueError("Unknown suite: " + args.suite)
                tasks = dataset["tasks"]
            if not tasks or len(tasks) != len(set(tasks)) or set(tasks) - set(dataset["tasks"]):
                raise ValueError("Task selection is empty, duplicated or not present in the frozen dataset")
            for task in tasks:
                load_task(PROJECT / "datasets" / dataset["sha256"] / "tasks" / task)
            if args.action != "run":
                result = {"framework": artifact, "dataset": dataset, "tasks": tasks, "profile_sha": config["profile_sha"]}
                if args.action == "plan":
                    plans = []
                    for task_id in tasks:
                        task = PROJECT / "datasets" / dataset["sha256"] / "tasks" / task_id
                        workdir = predict_workdir(task / "environment" / "Dockerfile")
                        mappings = make_mappings(workdir, config["path_policy"].get(task_id, {}).get("extra_roots", []))
                        destination = PROJECT / "cache" / "plans" / dataset["sha256"] / task_id
                        audit = adapt_task(task, destination, mappings)
                        plans.append({"task": task_id, "predicted_workdir": workdir, "audit": str(destination / "adaptation.json"), "skills": len(audit["provided_skills"])})
                    result["path_plans"] = plans
                write_json(PROJECT / "prepared.json", result)
                if args.action == "prepare" and args.pin_defaults:
                    saved = read_document(PROJECT / "evaluation.yaml")
                    saved["framework"] = "artifacts/" + artifact["sha256"]
                    saved["dataset"] = "datasets/" + dataset["sha256"]
                    (PROJECT / "evaluation.yaml").write_text(yaml.safe_dump(saved, sort_keys=False, allow_unicode=True), encoding="utf-8")
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return 0
            jobs = args.jobs or int(config.get("jobs", 2))
            if not 1 <= jobs <= 32:
                raise ValueError("jobs must be between 1 and 32")
            directory = create_run(PROJECT, config, artifact, dataset, tasks, jobs)
            effective = read_json(directory / "manifest.json")["jobs"]
            if effective != jobs:
                print(f"Shared quota caps task concurrency: requested={jobs}, effective={effective}. See profiles/model-quota.yaml.", flush=True)
            print("RUN_DIRECTORY=" + str(directory), flush=True)
            run_batch(PROJECT, directory, keep=args.keep_containers)
            return 0
        if args.run:
            directory = resolve_path(args.run)
            if not directory.is_dir():
                directory = PROJECT / "runs" / args.run
        else:
            directories = sorted((PROJECT / "runs").glob("*/manifest.json"))
            if not directories:
                raise ValueError("No evaluation runs yet")
            directory = directories[-1].parent
        if args.action == "report":
            print(json.dumps(generate_report(directory), ensure_ascii=False, indent=2))
        elif args.action == "stop":
            (directory / "STOP").write_text("stop requested\n", encoding="utf-8")
            print("Stop requested; active runs will cancel, archive evidence and close their own containers.")
        elif args.action == "status":
            manifest = read_json(directory / "manifest.json")
            rows = []
            for task in manifest["tasks"]:
                results = sorted((directory / "tasks" / task).glob("attempt-*/result.json"))
                latest = read_json(results[-1]) if results else {}
                rows.append({"task": task, "phase": latest.get("phase", "pending"), "outcome": latest.get("outcome"),
                             "score": latest.get("score"), "attempt": latest.get("attempt")})
            print(json.dumps({"run": str(directory), "status": manifest["status"], "model": manifest["model"], "tasks": rows}, ensure_ascii=False, indent=2))
        elif args.action == "resume":
            check_resume(directory)
            lock = directory / "runner.lock"
            if args.recover and lock.exists():
                pid = lock.read_text().strip()
                if os.name == "nt":
                    active = pid in command(["tasklist", "/FI", "PID eq " + pid, "/FO", "CSV", "/NH"], check=False).stdout.split('"')
                else:
                    try:
                        os.kill(int(pid), 0)
                        active = True
                    except ProcessLookupError:
                        active = False
                if active:
                    raise ValueError("Previous runner is still alive; refusing lock recovery")
                recover_containers(directory)
                lock.unlink()
            run_batch(PROJECT, directory, retry_errors=args.retry_errors)
        elif args.action == "analyze":
            from .analysis import analyze_failures
            from .gateway import ModelGateway
            manifest = read_json(directory / "manifest.json")
            settings = load_settings(PROJECT)
            manifest["quota"] = settings["quota"]
            manifest["analysis"] = settings["analysis"]
            gateway = ModelGateway(PROJECT, directory, manifest)
            try:
                if not args.evidence_only:
                    gateway.start()
                analyze_failures(PROJECT, directory, None if args.evidence_only else gateway, settings["analysis"])
            finally:
                gateway.close()
            print(json.dumps(generate_report(directory), ensure_ascii=False, indent=2))
        return 0
    except KeyboardInterrupt:
        print("Interrupted. Use status/resume to inspect and continue the batch.", file=sys.stderr)
        return 130
    except Exception as error:
        print(sanitize(str(error)), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
