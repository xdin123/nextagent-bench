# 本次两题补测的轨迹

本批次只包含人工批准的 `ada-bathroom-plan-repair` 和 `azure-bgp-oscillation-route-leak`。原全量批次保持 STOPPED，分数和冻结配置不变。

## 原生文件

每题的 `tasks/<task>/attempt-001/nextagent-home/logs/nextagent-plugin-diagnostic.*.ndjson` 由被测框架生成，完整原文件同时位于 `nextagent-home.tar` 中。评测器提取日志时不改写原行。

同一个文件包含两类记录：

- `pluginId=developer-hook-trace`、`payload.event=DEVELOPER_HOOK_TRACE`：本次恢复的调用边界 Hook，边界在 `payload.boundary`。
- `pluginId=framework-model-recovery`、`artifactType=model-recovery`：重复输出、输出容量及恢复诊断。

Agent 配置启用了六个阶段：`BEFORE_PLANNING`、`BEFORE_MODEL_INVOKE`、`AFTER_MODEL_RESULT`、`BEFORE_CAPABILITY_INVOKE`、`AFTER_CAPABILITY_RESULT`、`BEFORE_AGENT_TERMINAL`。正式请求和启动预检是两个不同请求，必须按各题 `result.json.requestId` 与 `priming.json.requestId` 区分。不能用预检成功出现的终态 Hook，声称失败的正式请求也出现过。

## 采集核验

`trace-coverage.json` 按正式请求记录实际阶段、原文件摘要和缺失项。配置启用六阶段不等于任意失败路径都会生成六阶段；例如 Azure 任务的 `MODEL_DUPLICATION_DETECTED` 终止路径没有正式请求的 `BEFORE_AGENT_TERMINAL` 记录。此缺口如实保留，不补造、不通过再次重跑填齐。

“完整 Hook”指恢复该插件的完整绑定并保存框架实际生成的数据，不表示无界 provider 原始流。框架自己的字段/行大小限制、脱敏和路径覆盖仍然适用。既有语义分析器尚未完整消费原生嵌套 payload，不能将自动分析报告视为已经分析了全部 Hook 边界。

原生轨迹之外，`trajectory.jsonl` 保存正式运行事件，`model-gateway/*/exchanges.tar` 保存本地模型交换证据，`nextagent-home.tar` 保存工作区、日志和运行状态。评分仍以原 verifier 和 result.json 为准。
