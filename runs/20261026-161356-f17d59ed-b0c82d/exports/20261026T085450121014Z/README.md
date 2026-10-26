# Completed native diagnostic export

completed-framework-traces.ndjson preserves each native plugin object and adds _bench task/attempt/source metadata.
All ended attempts are included, including history and preflight records. Use _bench.trace_scope=formal_task for task-only analysis.
attempt-index.csv lists every ended attempt, including environment failures without native traces.
recovery-task-index.csv and recovery-task-names.json distinguish direct terminal failures from observed recovery handling.
Output-capacity or duplication recovery events alone do not establish why the benchmark failed.
Ordering retains each file's original order, grouped by task and attempt. Use recordedAt for cross-task time analysis.
Original files and previous scores were not changed. Registered upstream credential values are redacted if present.

## 本次 Hook 采集范围

本次恢复 developer-hook-trace 六阶段绑定。合并文件有393行，其中119条开发 Hook 边界、274条模型恢复诊断。两题正式请求均因 MODEL_DUPLICATION_DETECTED 失败，没有正式请求的 BEFORE_AGENT_TERMINAL 记录；预检的终态记录不算正式任务覆盖。每题 trace-coverage.json 记录实际阶段和缺失项。原始 tar 与展开日志逐文件摘要一致；合并仅增加来源字段，并按既有导出策略检查凭据。
