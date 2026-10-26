"""Operator-controlled admission; completed attempts are never resubmitted."""
from __future__ import annotations

import concurrent.futures
import json
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


def pending_tasks(directory: Path, tasks: list[str], retry_errors: bool) -> list[str]:
    pending = []
    for task in tasks:
        results = sorted((directory / "tasks" / task).glob("attempt-*/result.json"))
        latest = read_json(results[-1]) if results else None
        if latest and latest.get("status") == "FINISHED" and latest.get("outcome") != "INTERRUPTED" and not (
            retry_errors and latest.get("outcome") in RETRYABLE_OUTCOMES
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
