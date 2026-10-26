# 单题评测产物阅读指南

适用批次：`20261025-195147-f17d59ed-c79fa2`。本文件只说明现有产物，不修改执行代码、冻结配置或评分。

## 1. 每题先看 result.json

每次尝试保存在 `tasks/<任务名>/attempt-xxx/`。排查最近执行看最新 attempt；旧 attempt 保留。正式汇总继续采用首次有效评分，不覆盖旧结果。

| 字段 | 用途 |
| --- | --- |
| `status`、`phase` | 判断正在排队、构建、预检、执行、评分还是已收尾。`FINISHED` 只表示本次尝试结束。 |
| `outcome`、`score` | 本次端到端结果和评分；`PASSED` 才是通过。`score: null` 表示尚无有效评分，不应自行按零分解释。 |
| `reward`、`verifier` | 原评分器给出的奖励及检查结果；原奖励和端到端 `score` 的语义不同。 |
| `failed_phase`、`error` | 构建、预检等异常发生在哪个阶段。 |
| `terminal.status`、`terminal.payload.code` | Agent 请求自身的终态和错误码。执行失败不一定有 `failed_phase`。 |
| `phase_seconds`、`budgets` | 分阶段耗时和原题资源/超时预算。活跃阶段的耗时通常在阶段切换时归约，不是连续刷新计时器。 |
| `artifact_errors`、`evidence_complete`、`home_archive` | 归档是否报错、容器证据采集状态及归档位置。采集标记不代表语义分析已经完整。 |

## 2. 按结果选择文件

| 情况 | 接下来重点看 | 文件缺失如何解释 |
| --- | --- | --- |
| `RUNNING` | `result.json` 的当前阶段；构建看 `environment-build.log`；正式执行看 `trajectory.jsonl` | 未进入的阶段没有对应文件；完整归档通常在收尾后出现。 |
| `ENVIRONMENT_ERROR`，`failed_phase=queued` | `result.json` 的资源拒绝原因和 `budgets` | 容器可能尚未创建，通常没有模型轨迹、原生日志或评分器结果。 |
| `ENVIRONMENT_ERROR`，`failed_phase=build` | `environment-build.log`；若失败在框架注入层，再看 `agent-layer-build.log` | 环境未准备好，缺少正式轨迹和评分结果是正常的。 |
| `ENVIRONMENT_ERROR`，`failed_phase=container_setup` | `container-start.log`，使用 Compose 的题看 `compose-start.log`；结合 `result.json` | 是否已有归档取决于容器是否成功创建及采集是否完成。 |
| `PREFLIGHT_ERROR` | `failed_phase`；启动看 `bootstrap.json` / `runtime/na-start.log`；工具预检看 `priming-trajectory.jsonl`；Skill 预检看 `skill-discovery.json` | 尚未进入正式任务时，没有 `trajectory.jsonl`、`ctrf.json` 或最终答复并不异常。 |
| `EXECUTION_FAILED` | `terminal.payload.code`、框架原生日志和 `trajectory.jsonl`；必要时关联模型交互抓包 | 请求执行失败不能仅凭最终答复或评分器日志判断责任方。 |
| `TASK_FAILED` | `ctrf.json`、`verifier-stdout.txt`、`verifier-logs/`，再对照答复和实际生成文件 | Agent 已结束但评分未通过；重点核对未满足的评分条件。 |
| `TIMEOUT` | `phase-timing.json`、原题预算、最后一段事件及框架日志 | 结合正式 Agent 阶段耗时判断超时，不能仅用含排队/构建的总时长。 |
| `INTERRUPTED` | 停止/中断阶段、旧 attempt 及后续恢复 attempt | 中断结果保留；恢复会新建 attempt。 |
| `PASSED` | `result.json`、`ctrf.json`、实际工作区产物；研究框架行为时再看原生日志 | 成功题不要求存在深度失败分析。 |

## 3. 各类文件承担什么作用

| 文件或目录 | 重点用途 |
| --- | --- |
| `nextagent-home/logs/nextagent-plugin-diagnostic.*.ndjson` | 框架插件原生诊断；当前样本包含模型调用、校验、重复输出检测与恢复决策等，记录在 `artifactType`、`payload.event`、`payload.snapshots` 等结构中。 |
| `nextagent-home/logs/nextagent-operational.log.*.jsonl` 及同目录其他日志 | 框架运行诊断及其他受控观测；根据字段定位模型与工具执行信息。不能认为插件诊断单个文件包含所有工具执行事实。 |
| `trajectory.jsonl` | 评测器采集的正式任务事件流，可追踪请求终态、工具调用、Skill 调用等。 |
| `priming-trajectory.jsonl` | 正式任务前的工具/工作区预检事件流；与正式执行分开阅读。 |
| `nextagent-home.tar` | 完整 home 归档。实际执行工作区在包内 `home/workspaces/execution/<scope>/workspace/`，用于检查生成的代码、表格、图片和输出文件。 |
| `nextagent-home/logs/` | 从上述归档单独展开的日志副本；该展开目录不包含完整工作区。 |
| `final-answer.txt` | Agent 的最终文字答复；生成的其他文件需到工作区归档检查。 |
| `ctrf.json`、`reward.txt`、`verifier-stdout.txt`、`verifier-logs/` | 原评分器的结构化结果、奖励和输出，核查为什么通过或未通过。 |
| `phase-timing.json` | 本次尝试收尾后的分阶段耗时，用于分析排队、构建、Agent 执行、评分和采集的耗时。 |
| `agent-facing/`、`path-bridge.json` | Agent 实际收到的适配输入、Skill 及路径桥接信息；用于排查题面、文件路径和实际执行工作区是否对应。 |
| `skill-catalog.json`、`skill-discovery.json` | Skill 是否可发现。实际调用/加载还需结合事件流及执行日志，不能仅凭目录或 catalog 存在判断已使用。 |
| `model-transport.json` | 模型路由及评测传输说明；不是完整模型请求/响应抓包。 |
| `runtime/na-start.log`、`bootstrap.json`、`container-inspect.json` | 框架启动、装配及容器资源配置排查。 |
| `failure-analysis.md` | 汇总导出时生成的基础说明和证据导航，成功题也可能存在。文件名不代表任务失败，也不代表已完成模型与框架的细粒度归因。 |
| `analysis/latest.json` | 最新一次深度诊断的入口，指向版本化分析目录。 |
| `analysis/<时间目录>/report.md`、`diagnosis.json`、`packet.json`、`deterministic-audit.json` | 深度诊断文字、结构化结论、证据包和确定性复核；各文件按实际分析进展产生。 |
| `tool-boundary-checks.json` | 分析过程中形成的工具调用边界对齐证据，不是每个任务执行时必有的文件。 |

模型原始交互证据是批次级归档，位于 `model-gateway/<网关会话>/exchanges.tar`，通过任务名及 attempt 关联。当前网关运行时先写容器内证据，收尾后导出。抓包对凭据脱敏并排除 provider reasoning。

## 4. 为什么 3d-scan-calc 的文件更多

- 它已经完成环境准备、预检、正式执行、评分、归档和汇总，所以这些阶段的产物已经齐备。
- 构建失败、资源不足、预检失败的题会较早退出，后续阶段的文件不会产生。
- 正在运行的题只包含当前已到达阶段的文件，归档及分阶段耗时文件通常在收尾后写入。
- 命中镜像缓存的题可能没有 `environment-build.log` 或 `agent-layer-build.log`；只有实际构建的阶段才写对应构建日志。
- 先前停机/汇总时已有的题可能多出 `failure-analysis.md` 或 `analysis/`；本次新结束的题尚未经过下一次汇总或分析时可能没有。
- Compose 题、恢复题和不同任务输入会产生各自专用文件，不能以文件总数判断证据是否齐全。

若任务已执行并收尾，却缺少预期归档，先检查 `result.json` 的 `artifact_errors`、`home_archive` 和 `evidence_complete`，再判断是阶段未到达还是采集异常。

## 5. 怎样使用深度分析结论

- `analysis/latest.json` 的 `status=ANALYSIS_INCOMPLETE`：分析未完成，不能把目录中的文字当作最终根因结论。
- `status=EVIDENCE_READY`：证据已整理，尚无完成的语义诊断。
- `status=SEMANTIC_ANALYSIS_COMPLETE`：语义分析已生成并通过结构校验；仍需看 `audit_status` 和对应证据，不等于根因已通过复现验证。
- `audit_status=REVIEW_REQUIRED`：需要进一步核实结论与确定事实的关系。
- 已登记的当前适配缺口：分析器尚未完整展开插件原生诊断的 `payload` / `snapshots`。这些原始文件已保留，模型恢复/校验相关诊断需对照它们复核；当前运行版本结束后再补适配，不改本轮执行或评分。详见批次根目录 `native-diagnostic-analysis-gap.json`。

## 6. 最短阅读路径

1. 看单题 `result.json`，确认 outcome、评分和失败阶段。
2. 评分未通过：看 `ctrf.json` 和评分器输出；执行异常：看框架原生日志与正式轨迹；构建异常：看构建日志。
3. 需要检查真正生成了什么文件：打开 `nextagent-home.tar` 内的执行工作区。
4. 需要初步归因：查看 `analysis/latest.json` 的状态，再读取对应分析报告和原始证据。

批次总表 `results.xlsx` / `report.md` 在导出或收尾时更新；运行中的单题当前状态以各自 `result.json` 为入口。
