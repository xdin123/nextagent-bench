# 两题诊断 Hook 补测结果

批次：`20261026-161356-f17d59ed-b0c82d`；状态：**FINISHED**。仅执行人工批准的两题，不继续原全量。

关联原批次：`20261025-195147-f17d59ed-c79fa2`。框架、题库、模型、系统配置和 verifier/oracle 沿用，恢复开发诊断 Hook，任务并发为2。原批次的首个有效分数和历史 attempt 不变。

| 任务 | 原首测分数 | 补测分数 | 终态错误码 | 开发 Hook 记录（含预检） |
|---|---:|---:|---|---:|
| ada-bathroom-plan-repair | 0 | 0 | MODEL_DUPLICATION_DETECTED | 78 |
| azure-bgp-oscillation-route-leak | 0 | 0 | MODEL_DUPLICATION_DETECTED | 41 |

## 查看轨迹

- [两题原生诊断合并 NDJSON](exports/20261026T085450121014Z/completed-framework-traces.ndjson)：393行，119条开发 Hook 边界、274条模型恢复诊断；每行增加 `_bench` 来源信息。
- [导出清单、摘要和范围说明](exports/20261026T085450121014Z/export-manifest.json)。
- [实际阶段覆盖核验](validation/native-trace-coverage.json)；[归档与展开文件摘要一致性](validation/archive-integrity.json)。
- 原生日志：`tasks/<task>/attempt-001/nextagent-home/logs/nextagent-plugin-diagnostic.2026-10-26.1.ndjson`。原始归档仍在同级 `nextagent-home.tar`。
- [补测 Excel](results.xlsx)；[运行报表](report.md)。

## 结论边界

六阶段 Hook 已恢复绑定，模型及工具边界确实采集。两题正式请求都在重复输出失败路径终止，未产生 `BEFORE_AGENT_TERMINAL` Hook；预检成功的终态记录不能替代正式请求。未补造缺失事件，未改框架产品代码。

两题的自动语义分析均为 `ANALYSIS_INCOMPLETE`，且既有分析器没有完整展开原生嵌套 payload。这里只确认终态码和已保存的证据，不把根因归为已定论；可直接使用上述原始轨迹继续人工分析。

本批次的 runner、模型代理和任务容器均已退出，报表已生成；没有创建新的定时监控，也不会自动重跑。
