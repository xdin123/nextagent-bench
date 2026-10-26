"""Operator-controlled admission; completed attempts are never resubmitted."""
from __future__ import annotations

import concurrent.futures
import json
import uuid
from collections import deque
from pathlib import Path

from .util import now, read_json, write_json

RETRYABLE_OUTCOMES = {"ENVIRONMENT_ERROR", "PREFLIGHT_ERROR", "HARNESS_ERROR", "VERIFIER_ERROR", "INTERRUPTED"}


def validate_jobs(value):
    if type(value) is not int or not 1 <= value <= 32:
        raise ValueError("Concurrency must be an integer from 1 to 32")
    return value


def read_concurrency(directory: Path, default: int) -> int:
    path = directory / "concurrency.json"
    return validate_jobs(read_json(path)["jobs"] if path.exists() else default)


def set_concurrency(directory: Path, jobs: int, reason: str) -> dict:
    validate_jobs(jobs)
    previous = read_concurrency(directory, read_json(directory / "manifest.json").get("jobs", 1)) if (directory / "manifest.json").exists() else 1
    value = {"jobs": jobs, "updated_at": now(), "reason": reason, "previous_jobs": previous,
             "scope": "Task admission and shared model concurrency only; frozen scoring inputs unchanged"}
    write_json(directory / "concurrency.json", value)
    with (directory / "concurrency-history.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False) + "\n")
    return value


def request_task_retries(directory: Path, tasks: list[str], reason: str) -> dict:
    """Persist an explicit, once-per-completed-attempt operator retry request."""
    if (directory / "runner.lock").exists():
        raise ValueError("Register precise retries only after the active runner has stopped")
    manifest = read_json(directory / "manifest.json")
    if not tasks or any(task not in manifest["tasks"] for task in tasks) or not reason.strip():
        raise ValueError("Explicit retries require known task names and a reason")
    path = directory / "task-retries.json"
    control = read_json(path) if path.exists() else {"run_id": manifest["run_id"], "tasks": {}}
    if control.get("run_id") != manifest["run_id"] or not isinstance(control.get("tasks"), dict):
        raise ValueError("Retry control belongs to another run or has invalid tasks")
    requests = {}
    request_id = uuid.uuid4().hex
    for task in dict.fromkeys(tasks):
        results = sorted((directory / "tasks" / task).glob("attempt-*/result.json"))
        latest = read_json(results[-1]) if results else None
        if latest and latest.get("status") != "FINISHED":
            raise ValueError("Selected task has an unfinished attempt: " + task)
        number = int(results[-1].parent.name.split("-")[-1]) if results else 0
        previous = control["tasks"].get(task)
        if previous and previous.get("after_attempt") == number:
            continue
        requests[task] = {"after_attempt": number, "reason": reason.strip(), "requested_at": now(), "request_id": request_id}
    if requests:
        control["tasks"].update(requests)
        write_json(directory / "retry-requests" / (request_id + ".json"),
                   {"run_id": manifest["run_id"], "tasks": requests})
        write_json(path, control)
    return control


def pending_tasks(directory: Path, tasks: list[str], retry_errors: bool) -> list[str]:
    pending = []
    path = directory / "task-retries.json"
    retries = read_json(path).get("tasks", {}) if path.exists() else {}
    if not isinstance(retries, dict) or any(task not in tasks for task in retries):
        raise ValueError("Invalid explicit retry task selection")
    for task in tasks:
        results = sorted((directory / "tasks" / task).glob("attempt-*/result.json"))
        latest = read_json(results[-1]) if results else None
        number = int(results[-1].parent.name.split("-")[-1]) if results else 0
        retry = retries.get(task)
        if retry and (not isinstance(retry, dict) or type(retry.get("after_attempt")) is not int or retry["after_attempt"] < 0):
            raise ValueError("Invalid explicit retry attempt for " + task)
        selected = retry is not None and number <= retry["after_attempt"]
        if latest and latest.get("status") == "FINISHED" and latest.get("outcome") != "INTERRUPTED" and not (
            selected or retry_errors and latest.get("outcome") in RETRYABLE_OUTCOMES
        ):
            continue
        pending.append(task)
    return pending


def dispatch_tasks(directory: Path, tasks: list[str], default: int, worker, apply_limit):
    pending, active, applied = deque(tasks), set(), None
    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as pool:
        try:
            while pending or active:
                target = read_concurrency(directory, default)
                if target != applied:
                    apply_limit(target)
                    applied = target
                    write_json(directory / "concurrency-applied.json", {"jobs": target, "applied_at": now()})
                draining = (directory / "DRAIN").exists() or (directory / "STOP").exists()
                while pending and len(active) < target and not draining:
                    active.add(pool.submit(worker, pending.popleft(), target))
                if not active:
                    break
                done, active = concurrent.futures.wait(active, timeout=0.25, return_when=concurrent.futures.FIRST_COMPLETED)
                for future in done:
                    future.result()
        except BaseException:
            (directory / "STOP").write_text("Scheduler interrupted; archive active work before resuming.\n", encoding="utf-8")
            raise
