from __future__ import annotations

import math
from collections import Counter

from .util import digest


def resume_identity(manifest: dict) -> str:
    fields = ("framework_sha", "dataset_sha", "profile_sha", "adapter_sha", "model", "base_url", "tasks", "skill_mode")
    return digest({key: manifest.get(key) for key in fields})


def summarize_verifier(reward_text: str, ctrf: dict, exit_code: int) -> dict:
    tests = ctrf.get("results", {}).get("tests", [])
    failed = [test.get("name", "unknown") for test in tests if test.get("status") in {"failed", "broken"}]
    try:
        reward = float(reward_text.strip())
        if not math.isfinite(reward) or not 0 <= reward <= 1:
            raise ValueError("reward outside [0,1]")
    except (ValueError, AttributeError):
        return {"outcome": "VERIFIER_ERROR", "reward": None, "failed_tests": failed, "exit_code": exit_code}
    return {"outcome": "PASSED" if reward == 1 else "TASK_FAILED", "reward": reward, "failed_tests": failed, "exit_code": exit_code}


def event_metrics(events: list[dict]) -> dict:
    steps, skills, loaded, counts = set(), set(), set(), Counter()
    for event in events:
        kind, payload = event.get("eventType"), event.get("payload") or {}
        counts[kind] += 1
        if kind in {"LLM_CONTENT_DELTA", "LLM_THINKING_DELTA"} and payload.get("stepId"):
            steps.add(payload["stepId"])
        if payload.get("capabilityId") == "Skill":
            target = payload.get("targetCapabilityId") or payload.get("capabilityTargetName") or payload.get("capabilitySubjectName")
            if target and kind == "CAPABILITY_STARTED":
                skills.add(target)
            if target and kind == "CAPABILITY_COMPLETED" and payload.get("status") == "SUCCEEDED":
                loaded.add(target)
    return {"model_rounds": len(steps), "tool_calls": counts["CAPABILITY_STARTED"],
            "skills_invoked": sorted(skills), "skills_loaded": sorted(loaded), "event_counts": dict(counts)}
