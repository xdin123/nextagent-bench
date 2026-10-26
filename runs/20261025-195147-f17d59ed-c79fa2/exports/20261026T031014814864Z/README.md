# Completed native diagnostic export

completed-framework-traces.ndjson preserves each native plugin object and adds _bench task/attempt/source metadata.
All ended attempts are included, including history and preflight records. Use _bench.trace_scope=formal_task for task-only analysis.
attempt-index.csv lists every ended attempt, including environment failures without native traces.
recovery-task-index.csv and recovery-task-names.json distinguish direct terminal failures from observed recovery handling.
Output-capacity or duplication recovery events alone do not establish why the benchmark failed.
Ordering retains each file's original order, grouped by task and attempt. Use recordedAt for cross-task time analysis.
Original files and previous scores were not changed. Registered upstream credential values are redacted if present.

## Collection scope caveat

The batch explicitly excluded the developer-hook-trace.loop-raw-boundary Agent hook. The exported native files observed here contain framework-model-recovery/model-recovery records, not a complete developer-hook-trace boundary transcript. Parsing existing records cannot reconstruct the uncollected hook events. See diagnostic-format-review/findings.json in the batch directory.
