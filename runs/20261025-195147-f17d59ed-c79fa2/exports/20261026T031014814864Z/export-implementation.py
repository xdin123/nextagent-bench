"""Export preserved native plugin traces without reading or printing their payloads."""
from __future__ import annotations

import argparse
import collections
import csv
import datetime
import gzip
import hashlib
import json
import os
from pathlib import Path


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def csv_file(path: Path, rows: list[dict], columns: list[str]):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    run = args.run.resolve()
    manifest = load(run / "manifest.json")
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output = run / "exports" / stamp
    output.mkdir(parents=True)
    secrets = [item["key"] for item in json.loads(os.environ.get("NAB_API_KEYS", "[]")) if item.get("key")]
    attempts, source_files, invalid, recovery = [], [], [], []
    merged = output / "completed-framework-traces.ndjson"
    total = 0
    redactions = 0
    scopes = collections.Counter()
    with merged.open("w", encoding="utf-8", newline="\n") as target:
        for result_file in sorted(run.glob("tasks/*/attempt-*/result.json")):
            result = load(result_file)
            if result.get("status") != "FINISHED":
                continue
            attempt = result_file.parent
            priming = load(attempt / "priming.json") if (attempt / "priming.json").exists() else {}
            counts = collections.Counter()
            diagnostic_files = sorted(p for p in (attempt / "nextagent-home/logs").glob("nextagent-plugin-diagnostic.*.ndjson*")
                                      if p.name.endswith((".ndjson", ".ndjson.gz")))
            records = 0
            for source in diagnostic_files:
                relative = source.relative_to(run).as_posix()
                source_hash = sha(source)
                source_count = 0
                opener = gzip.open if source.suffix == ".gz" else open
                with opener(source, "rt", encoding="utf-8-sig", errors="strict") as stream:
                    for line_number, line in enumerate(stream, 1):
                        if not line.strip():
                            continue
                        for secret in secrets:
                            count = line.count(secret)
                            if count:
                                line = line.replace(secret, "<redacted>")
                                redactions += count
                        try:
                            value = json.loads(line)
                            if not isinstance(value, dict) or "_bench" in value:
                                raise ValueError("Expected original object without reserved _bench metadata")
                        except ValueError as error:
                            invalid.append({"source_file": relative, "source_line": line_number,
                                            "error_type": type(error).__name__})
                            continue
                        request_id = value.get("requestId")
                        scope = "formal_task" if request_id and request_id == result.get("requestId") else (
                            "workspace_preflight" if request_id and request_id == priming.get("requestId") else "other_or_unknown")
                        value["_bench"] = {"run_id": manifest["run_id"], "task": result["task"],
                                           "attempt": result["attempt"], "outcome": result.get("outcome"),
                                           "score": result.get("score"), "trace_scope": scope,
                                           "source_file": relative, "source_line": line_number}
                        target.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")
                        source_count += 1
                        records += 1
                        total += 1
                        scopes[scope] += 1
                        payload = value.get("payload") or {}
                        if scope != "formal_task" or not isinstance(payload, dict):
                            continue
                        event, kind, action = payload.get("event"), payload.get("kind"), payload.get("action") or ""
                        if action == "STOP_DUPLICATE_STREAM" or (event == "model.recovery.detected" and kind == "DUPLICATION"):
                            counts["duplication_detected_records"] += 1
                        if kind == "OUTPUT_CAPACITY" and not str(action).startswith("CHECK_") and (
                            event in {"model.recovery.action", "model.recovery.detected", "model.recovery.finished"}):
                            counts["output_capacity_handling_records"] += 1
                source_files.append({"file": relative, "sha256": source_hash, "bytes": source.stat().st_size,
                                     "exported_records": source_count})
            terminal = result.get("terminal") or {}
            code = (terminal.get("payload") or {}).get("code") or ""
            row = {"task": result["task"], "attempt": result["attempt"], "outcome": result.get("outcome"),
                   "score": result.get("score"), "terminal_status": terminal.get("status"), "terminal_code": code,
                   "native_files": len(diagnostic_files), "native_records": records,
                   "duplication_detected_records": counts["duplication_detected_records"],
                   "output_capacity_handling_records": counts["output_capacity_handling_records"],
                   "terminal_duplication_failure": code == "MODEL_DUPLICATION_DETECTED",
                   "terminal_output_capacity_failure": any(term in code for term in ["OUTPUT_CAPACITY", "OUTPUT_TOO_LONG", "OUTPUT_LIMIT", "MAX_OUTPUT_TOKENS"]),
                   "result_file": result_file.relative_to(run).as_posix()}
            attempts.append(row)
            if row["terminal_duplication_failure"] or row["terminal_output_capacity_failure"] or any(counts.values()):
                recovery.append(row)
    columns = ["task", "attempt", "outcome", "score", "terminal_status", "terminal_code", "native_files", "native_records",
               "duplication_detected_records", "output_capacity_handling_records", "terminal_duplication_failure",
               "terminal_output_capacity_failure", "result_file"]
    csv_file(output / "attempt-index.csv", attempts, columns)
    csv_file(output / "recovery-task-index.csv", recovery, columns)
    names = {
        "terminal_duplication_failure_tasks": sorted({r["task"] for r in recovery if r["terminal_duplication_failure"]}),
        "terminal_output_capacity_failure_tasks": sorted({r["task"] for r in recovery if r["terminal_output_capacity_failure"]}),
        "formal_output_capacity_handling_tasks": sorted({r["task"] for r in recovery if r["output_capacity_handling_records"]}),
        "formal_duplication_detected_tasks": sorted({r["task"] for r in recovery if r["duplication_detected_records"]}),
        "interpretation": "Observed recovery handling is not proof it caused a task failure. Terminal codes identify direct termination; causal attribution still requires snapshot and tool/provider evidence. Preflight records are excluded from these task-level handling sets."
    }
    (output / "recovery-task-names.json").write_text(json.dumps(names, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {"run_id": manifest["run_id"], "created_at": stamp, "merged_file": str(merged),
               "merged_sha256": sha(merged), "merged_bytes": merged.stat().st_size, "records": total,
               "ended_attempts": len(attempts), "tasks_with_records": len({r["task"] for r in attempts if r["native_records"]}),
               "attempts_with_records": sum(bool(r["native_records"]) for r in attempts), "source_files": source_files,
               "trace_scopes": dict(scopes), "registered_credential_redactions": redactions, "invalid_lines": invalid,
               "ordering": "task_id, attempt_directory, source_file, source_line; original per-file order retained",
               "record_format": "Original framework object with additional _bench provenance; native source files unchanged",
               "selection": "All attempts with result.status=FINISHED, including failed and interrupted attempts; source-less attempts listed in attempt-index.csv",
               "export_script_sha256": sha(Path(__file__))}
    (output / "export-manifest.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "export-implementation.py").write_bytes(Path(__file__).read_bytes())
    (output / "README.md").write_text(
        "# Completed native diagnostic export\n\n"
        "completed-framework-traces.ndjson preserves each native plugin object and adds _bench task/attempt/source metadata.\n"
        "All ended attempts are included, including history and preflight records. Use _bench.trace_scope=formal_task for task-only analysis.\n"
        "attempt-index.csv lists every ended attempt, including environment failures without native traces.\n"
        "recovery-task-index.csv and recovery-task-names.json distinguish direct terminal failures from observed recovery handling.\n"
        "Output-capacity or duplication recovery events alone do not establish why the benchmark failed.\n"
        "Ordering retains each file's original order, grouped by task and attempt. Use recordedAt for cross-task time analysis.\n"
        "Original files and previous scores were not changed. Registered upstream credential values are redacted if present.\n", encoding="utf-8")
    print(json.dumps({"output_directory": str(output), "merged_file": str(merged), "records": total,
                      "merged_bytes": merged.stat().st_size, "ended_attempts": len(attempts),
                      "tasks_with_records": summary["tasks_with_records"], "attempts_with_records": summary["attempts_with_records"],
                      "invalid_lines": len(invalid), "credential_redactions": redactions, **names}, ensure_ascii=True))


if __name__ == "__main__":
    main()
