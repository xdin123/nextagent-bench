# NextAgent / SkillsBench 评测复盘与长期运行方案

日期：2026-10-25。本文是分析与建议，不代表已修改驱动或已验证新方案性能。

## 结论

当前评测已经能完成部分任务，但尚不适合作为长期版本对比基线。优先问题是评测有效性、批次隔离和失败归因；随后再处理缓存、并发和模型开销。

用户所说的“30销售”在本文按“30小时”理解。session 中的 25～30 小时来自逐题串行外推，记录里没有一轮成功完成全部 87 题的实测总时长。不能把首次搭建、人工诊断、无效运行和正式评测混在一起计时。

推荐路线：固定 BenchFlow 版本并使用其已有调度、恢复、任务解析与结果机制，保留一个 NextAgent 专用适配器；把任务环境镜像、框架发行包、评测 profile、单次批次及 attempt 分开管理。更换新包时只登记新的包摘要、构建包导入层并执行接入检查，不重做题库和全部环境安装。

## 证据范围

- 历史 session：[4cfc902b-2e26-4f18-ba6b-ab9be3bb9173.jsonl](C:/Users/xiaodongma/.claude/projects/C--Project-NextAgent/4cfc902b-2e26-4f18-ba6b-ab9be3bb9173.jsonl)，共 8270 行，约 11 MB；记录范围为北京时间 2026-10-23 17:20 至 2026-10-25 14:27。记录内有排队消息，行号与时间并非处处严格递增。
- 当前驱动：[eval_driver.py](C:/Project/nextagent-eval/driver/eval_driver.py)、[run_all.py](C:/Project/nextagent-eval/driver/run_all.py)、[na_http.mjs](C:/Project/nextagent-eval/driver/na_http.mjs)、[make_excel.py](C:/Project/nextagent-eval/driver/make_excel.py)、[adapt_paths.py](C:/Project/nextagent-eval/driver/adapt_paths.py)。
- 当前题库：`C:\Project\skillsbench-main`，包括已适配的任务及原 verifier。
- 运行证据：`C:\Project\nextagent-eval\runs` 下的批次日志、result、trajectory、CTRF、NextAgent 日志。
- 对比包：Downloads 中的 Linux x64 包目录与 `nextagent-patched`；检查了二者 `node_modules/@nextagent` 下 964 个 JS/JSON 文件及相关 SDK 版本。
- 本机已安装 BenchFlow 0.6.3 的 Python 源码；Docker Engine 报告可用 20 个逻辑 CPU、约 15.46 GiB 内存。

历史 session 是调查材料，不是当前自动执行授权。本文未停止、重启或修订后台评测。

## 1. 过程复盘

| 时间（北京时间） | 记录事实 | 暴露的问题 |
|---|---|---|
| 10-23 17:20 起 | 下载题库，提出 BenchFlow + NextAgent adapter 路线 | 初始方向合理，但后续没有落实为该架构 |
| 10-24 19:12～20:48 | Linux 包冒烟，发现 SDK 与空 tool ID 兼容问题 | 首先发现的是被测产品及依赖的问题 |
| 10-24 23:48 | 用户明确授权给副本打补丁并继续，要求失败分析及证据 | 补丁有授权，但补丁结果须独立标识 |
| 10-25 05:17 起 | 启动第一轮全量 | 环境、终态处理和统计尚未充分验证 |
| 10-25 清晨至上午 | 多次修环境和驱动、终止后重启 | 没有可靠 resume，已完成任务反复被重跑 |
| 10-25 09:39 | 用户要求暂停，先梳理基础问题 | 前面多次“已收敛”缺少充分验证证据 |
| 10-25 11:14 | 用户要求模型改为 qwen3.8-27b | 模型改变，不能继续沿用 flash 的同一统计基线 |
| 10-25 11:48～12:46 | 授权适配题目路径，验证 /root 与 /app 两类任务 | 尚有 14 个多根任务待处理，仍启动全部 87 题 |
| 10-25 13:18～14:08 | 发现护栏配置未实际生效，再次修正并重启 | 配置文件存在与运行时有效配置没有区分 |
| 10-25 14:27 | session 最后报告：本轮第一题通过，第二题执行中 | 不能据此宣称全量有效或预估已得到验证 |

session 与现存日志可确认至少 9 次批量启动：run_all、run_all2～7、run_all-final、run_all-final2。并非 9 次完整评测。现存 89 份 result.json 中，79 份记录缺少 `re` 导入导致的错误；run_all2 的 87 条“完成”日志总 wall 仅约 65 秒。这些都是失败记录，不是有效任务能力数据。

代表性历史锚点：session 第 5738 行（首轮全量）、6287 行（事件分页修复后重启）、6524 行（遗漏 guard 终态）、7098 行（承认驱动问题）、7168 行（暂停复盘）、8093 行（多根未适配仍全量）、8149 行（配置未加载）、8227 行（重复检测错误归为服务端瞬时问题）。

## 2. 当前存在的问题

### 2.1 Skills 复制成功，没有证明 Skills 已进入发现体系

`eval_driver.py:219` 的 align 在应用启动及 priming 之后才把题目 Skills 复制到 `NEXTAGENT_HOME/skills`。NextAgent 的 system-local discovery 采用 EAGER 扫描，并在 `agent-capability/dist/local/skill-discovery.js:654` 缓存扫描结果。

本次检查的 ADA 题，三个 Skill 目录已存在；日志中的 registered 仅有 `skill-creator`、`skill-diagnostics`，没有题目 Skill ID，也没有 Skill 工具调用记录。结合时序与缓存实现，题目 Skills 没有进入预期发现目录的风险很高；不能把文件复制或 task reward=1 当成 with-skill 生效证据。未调用 Skill 本身不必判任务失败，但预期 Skill 不可发现属于评测接入无效。

修正：系统 Skill 在启动前完整准备；接入检查通过公共目录/诊断接口确认应有 Skill 可发现。若该发行包没有可用查询接口，应明确标为待验证，不能用内部文件复制成功代替。再用独立接入 fixture 验证一次 Skill 加载和资源读取。保留 provided、discoverable、loaded、invoked 四种不同事实。

### 2.2 把被测框架失败排除出任务分，会掩盖评测目标

`eval_driver.py:336` 把所有 REQUEST_FAILED 统一记为 infra、reward=N/A，并跳过 verifier；重试列表还包含 INTERNAL_ERROR、MODEL_TOOL_ARGUMENTS_INVALID、MODEL_DUPLICATION_DETECTED。

这些 code 不能直接证明是外部基础设施故障。例如 NextAgent 的 `agent-model/dist/duplication-detection/controller.js:4` 在本地构造 MODEL_DUPLICATION_DETECTED，且标记 retryable=false。历史 session 将其解释为“qwen 请求过多/生成异常，瞬时问题”，证据不足；也不能直接等同 HTTP 429。

建议分别记录 harness/environment/framework/model/task/verifier/timeout/cancelled 等归因。归因未确认时保留 unknown 与证据。正式端到端成功率必须反映框架及模型执行失败，不能只计算走到 verifier 的幸存任务。环境或 harness 无效运行应单列数量与覆盖率，并补测；若保留“排除外部错误后的分数”，须与端到端结果同时展示分母。

### 2.3 重试会扩大预算并继承旧产物

`run_prompt` 每次只新建 session，复用同一容器、workspace、应用数据与 memory；每次又获得完整 timeout。若前一轮已写了一半输出，后一轮可继承。轨迹固定写 `trajectory.jsonl`，前一次内容被覆盖。一次题目在驱动层可能获得约 3×3600 秒，框架内部还有恢复机制。

修正：正式主结果固定 attempt 口径；外部瞬时故障按证据有限重试，所有重试共享题目总预算。需要独立重跑时使用干净容器和全新数据，并保留每个 attempt。沿用中间状态只能作为明确标识的恢复实验。诊断重跑与正式首次结果分开，不能用最后一次成功替换首次失败。

### 2.4 超时与资源没有遵守任务声明

`yaml_safe_load` 没有正确构造嵌套 YAML：实际解析 ADA 题得到 `agent={}`，2400.0 出现在顶层；于是驱动采用默认 3600 秒。verifier 固定 1800 秒、build 固定 1800 秒，也没有完整使用任务元数据。

容器实际 MemoryLimit=0、NanoCpus=0，而 ADA 题声明 1 CPU/4096 MB。并发前必须纠正，否则任务会竞争资源，结果边界也不可比较。

修正：使用 BenchFlow 的 task document 解析，读取各阶段预算；记录实际执行的限制。超时时取消 run，并确认执行停止后再验证或归档。当前 HTTP helper 超时只停止等待，可能在 Agent 仍写文件时启动 verifier，结果会发生竞争。

### 2.5 批次、框架版本、模型与历史结果混在一起

`run_all.py:31` 从共享 runs 根按任务名寻找最近一个有 result.json 的目录。当前 attempt 尚无 result 时可能回退到旧结果；Excel 又按 task 去重，只保留最后一条。batch-summary 在多次重启前被删除，缺少稳定批次边界。

修正：每批有独立 run-id，每次尝试有独立 attempt 目录。父进程知道并只读取此次子进程的确切结果路径。恢复仅允许批次配置一致，不能跨模型、框架包或 adapter 版本继承完成状态。记录产品包摘要、题库摘要、adapter 版本、profile、模型参数、任务集及环境镜像身份；摘要用于常规追溯，无需额外签名或复杂证明链。

### 2.6 框架代码、配置与运行文件共用可写挂载

实际框架目录固定为 nextagent-patched；所有题目把它可写挂到 `/opt/nextagent`。启动会复制 na-start.mjs 到该目录，并清理共用 run/pid。直接并发会产生共享写入、删除 pid 与包替换竞争；当前代码的固定容器名也无法并行跑同题不同版本或 attempt。

修正：运行批次引用固定包摘要的镜像/内容，代码层冻结，每题独立可写运行层和数据目录，资源名含 run/task/attempt。用镜像层共享代码，每个容器自己的写层隔离运行状态。新包导入后启动新批次，禁止在运行中的旧挂载目录覆盖文件。

### 2.7 题库适配没有完整证明语义等价

路径适配有用户明确授权，并非擅自改变任务。但应保存原始题库与可审阅适配差异。当前脚本会扫描题目及 Skill 文本并替换路径；其根目录识别依赖正则，不能可靠处理多 WORKDIR、多阶段 Dockerfile、相对 WORKDIR、多个数据根或所有 URL/代码路径语义。

已有记录明确 14 个多根任务尚未适配就进入全量，后续失败会混入框架能力分数。修改 prompt 还不足以证明 Skill 脚本、数据路径与 verifier 可达性一致。

修正：保存固定上游快照；以版本化适配副本应用修改。运行目录优先读取已构建镜像的最终配置，再用实际文件检查验证。为多根任务写明确映射与验收；未支持的任务保留可见的接入状态和覆盖率，不能静默排除，也不能先当 Agent 失败。环境/映射改变后用原 oracle 在独立验证容器复验，题目 verifier 不进入 Agent 执行区。

### 2.8 环境安装本身可能改变题目

当前每题安装 Node 到 `/usr/local`，可能覆盖题目自己的 Node；Dockerfile 通用插入与系统包兜底失败还会被 `|| true` 吞掉。历史发生过 Debian 镜像注入 Ubuntu 源等错误。

修正：保留原任务基镜像和运行依赖，Agent 专用 Node 放独立前缀并显式启动，不覆盖任务环境的 Node。环境准备独立构建并验证，使用缓存；发现不兼容镜像时单题明确失败，不继续带病跑模型。

### 2.9 异常落盘与取消不完整

result.json 只在 main 最后写；进程被终止时没有阶段结果。异常分支未统一收集产物/关闭应用/清理容器。多处 docker cp 仅检查是否抛 Python 异常，没有检查返回码；verifier 末尾 `true` 吞掉退出状态。最终 phase=done 不能证明 reward、CTRF、轨迹或快照齐备。

修正：阶段状态增量落盘，事件轨迹持续追加；finally 中先保存可用证据再清理。保留 verifier 原始退出码、输出与 reward，区分断言失败、验证器安装失败、验证器超时及文件缺失。缺证据显式标记，不能默认为成功采集。

### 2.10 Excel 的部分字段不是可靠测量

- `make_excel.py:103` 使用不存在的 `test.passed`；实际 CTRF 用 `status: passed`。检查到 reward=1 的 3D 任务中，两个通过用例都会被该逻辑列入 failed_test_names。
- `:164` 将模型写死为 qwen3.8-flash，当前实际使用 qwen3.8-27b。
- `:115`～`:123` 将 startedAt 到 finishedAt 的整段总耗时写作 Agent 耗时，包含 build/setup 等。
- token 列始终为空，skills_desc 列未填。
- “原因分析/证据”主要是失败用例拼接或通用 infra 描述，没有兑现用户要求的日志、轨迹、框架代码风险及可定位证据分析。

修正：报表作为结构化事实的派生结果，可重复生成。失败分析区分现象、已证实根因、候选假设、证据路径/事件坐标及建议；证据不足则明确写未知。输入/输出 token 从每个实际 invocation 的 normalized usage 汇总，缺失保持未知，避免流式重复累计与 priming 混入。

### 2.11 用活动日志判断“健康推进”证据不足

历史多次因 gateway.operation 仍输出就判断 Agent 没有卡住；但 HTTP 轮询本身就会触发 gateway 读取。model.recovery 的流程事件数还一度被解释为恢复次数，后来才纠正。

修正：区分服务存活、run 状态和业务进展。报告最近一次模型完成、工具完成、终态/取消、产物变更和阶段预算。reasoning 等有效模型进展要按产品 contract 判断，不能凭网关日志新鲜就断言任务在前进。运维应由落盘状态和受管理 runner 驱动；聊天定时检查用于解释异常，不能成为唯一进程监督机制。

### 2.12 运行配置与凭据不可隐式继承

护栏关闭有历史授权，但曾两次因 Agent root/优先级导致文件改动没有生效。启动还自动删除了一个诊断 hook；“之前没有事件”不足以证明删除没有观测损失。脚本中存在明文 API key 默认值，历史监控 prompt 也携带了 key。

修正：新包检查有效 Agent、模型和配置，而不只检查文件存在。配置策略明确为版本化 profile：部署包默认行为与能力评测行为分别记录；guard=false 等设置不得混成生产默认。新包不自动继承旧补丁或删除 hook；必要覆盖须列出差异。凭据只在启动时注入，不写源码、镜像、manifest、报告和监控文本；清理现有硬编码，按凭据管理流程处理已经持久化的密钥。

## 3. 耗时的实际证据

选取完成且有完整轨迹的 `3d-scan-calc-20261025-140900`：

| 阶段 | 秒 | 占总耗时 |
|---|---:|---:|
| result.startedAt 到 REQUEST_ACCEPTED | 260.489 | 37.7% |
| REQUEST_ACCEPTED 到 REQUEST_COMPLETED | 417.122 | 60.4% |
| 终态到 finishedAt | 13.389 | 1.9% |
| 合计 | 691.000 | 100% |

本题正式 request 的 24 条 model.invocation.summary 的 durationMs 合计约 404.446 秒，占 Agent 执行时间约 97%。这是该样本的观测，不能直接外推所有题。提交前 260 秒包含构建、Node 安装、启动、priming 和对齐，当前没有足够阶段计时进一步精确拆分。

同题另外两次完成运行总耗时约 498 秒、384 秒，正式 request 约 236 秒、224 秒，模型汇总约 231 秒、216 秒。说明任务执行存在模型循环次数和服务延迟波动，固定题目的历史耗时也不是常数。

证据：[result.json](C:/Project/nextagent-eval/runs/3d-scan-calc-20261025-140900/result.json)、[trajectory.jsonl](C:/Project/nextagent-eval/runs/3d-scan-calc-20261025-140900/trajectory.jsonl)、[operational log](C:/Project/nextagent-eval/runs/3d-scan-calc-20261025-140900/na-home/logs/nextagent-operational.log.1.jsonl)。createdAt 为毫秒 Unix 时间，result 本地时间按 Asia/Shanghai 解释。

## 4. 长期方案：换新编译包的固定流程

### 4.1 最少必要分离

1. 题库：固定上游快照、适配版本、任务清单与原 verifier。
2. 环境：原任务镜像加 Agent 专用 Node 等必要运行层，按构建输入缓存。
3. 被测产品：原始 tar.gz、候选 manifest、内容摘要。包内已知数据/log/workspace 不自动带入正式运行数据。
4. 评测配置：有效模型、参数、Skill mode、guard/diagnostic 设置、预算与重试规则。
5. 运行结果：每个 run/task/attempt 的状态、轨迹、日志、输出、verifier 和分析。

推荐目录仅作为管理示意，不是已经实现的接口：

```text
nextagent-eval/
  adapter/                    NextAgent 接入代码，版本化
  profiles/                   正式/快速回归的明确参数
  artifacts/<framework-sha>/   原始包与构建元数据
  datasets/<dataset-id>/       固定任务与适配差异
  runs/<run-id>/
    manifest.json             完整批次身份，不存密钥
    tasks/<task>/attempt-001/
      result.json
      phase-timing.json
      trajectory.jsonl
      nextagent-logs/
      outputs/
      verifier/
```

### 4.2 每次换包

1. 输入新 tar.gz 路径并计算内容摘要；读取实际 manifest 与 Node 要求，不根据目录名字猜版本，不绑定旧 candidateId。
2. 将原始包导入 Docker 镜像层。更换产品包只更新产品导入层；沿用有效的任务环境缓存。
3. 为各任务创建新容器及独立运行数据；执行期间引用固定镜像内容，避免 Windows 上覆盖挂载目录改变被测代码。
4. 在应用启动前放好有效 Agent 定义、配置和题目系统 Skills；保留配置差异及有效加载结果。包内原始配置按其完整配置语义加载，不假定自动 merge。
5. 接入检查覆盖原生启动入口、模型工具流式调用、有效配置、Skill 发现/读取、路径输入输出、终态和取消。已知包缺陷形成单独缺陷证据；正式结果不自动打旧补丁。
6. 新包建立新 run-id。与上一个包按相同任务、模型、profile、adapter、预算和环境比较。改变其中任一项时明确展示差异，必要时重测基线。

调试补丁仍可有价值：应另建包身份/批次，保存具体 diff，并与正式发行包结果并列。不能依靠一个不断覆盖的 nextagent-patched 目录代表所有版本。

### 4.3 复用已有 runner

本机 BenchFlow 0.6.3 的源码已包含 protocol=session-factory、并发、build_concurrency、resume、retry 和结果汇总。NextAgent 不需要新增 ACP 产品接口；评测端可以实现 Session 的 prompt/cancel/steps 等适配。

推荐固定当前验证过的 BenchFlow 版本，完成 NextAgent adapter，使用其调度与结果生命周期；当前 HTTP helper 中已验证的调用逻辑可以迁移。仍需检查 runner 的默认重试/评分是否符合本报告口径，不能认为使用官方工具便自动满足 NextAgent 评测要求。迁移先验证单题输出一致性，再小批量并发，不在后台正式批次中途切换。

参考：[本机 Agent registry](C:/Project/skillsbench-main/.venv/Lib/site-packages/benchflow/agents/registry.py:259)、[Session protocol](C:/Project/skillsbench-main/.venv/Lib/site-packages/benchflow/agents/protocol.py:105)、[Evaluation](C:/Project/skillsbench-main/.venv/Lib/site-packages/benchflow/evaluation.py:1)。官方源代码也提供 [registry](https://github.com/benchflow-ai/benchflow/blob/main/src/benchflow/agents/registry.py) 与 [evaluation](https://github.com/benchflow-ai/benchflow/blob/main/src/benchflow/evaluation.py)；实现时以锁定版本为准。

## 5. 提效顺序

| 优先级 | 做法 | 预期收益与边界 |
|---|---|---|
| P0 | 先完成不调用模型的 harness 契约检查 | 提前发现 YAML、终态分页、取消、CTRF、采集错误；避免全量充当驱动调试环境 |
| P0 | run/attempt 隔离、断点恢复、有效性检查 | 修一题不重跑全部，不混入旧结果 |
| P1 | 环境与 Node 构建缓存，框架放镜像层，运行数据放 Linux 本地卷 | 减少每题下载、跨 Windows 文件系统读取及启动准备开销 |
| P1 | 在隔离完成后先以 2 个任务并发试跑 | 缩短墙钟时间；检查模型 RPM/TPM、429、尾延迟和内存，再决定提高并发 |
| P1 | 统一总 deadline、有限外部重试 | 避免同题三倍预算、框架与驱动多层重试放大 |
| P2 | 固定快速回归子集，完整基线保留全量 | 日常获得快速信号；子集结果不冒充完整分数 |
| P2 | 分析模型调用次数、输入 token、工具错误和长尾 | 找到重复探索/失败循环；行为或配置优化作为新的显式实验，不静默改变主基线 |
| P2 | 已保存产物的重新判分与报告重生成 | verifier/报表修复无需再次调用 Agent；明确标记重判分版本 |

当前 Docker 可用内存约 15.46 GiB，部分题声明 4 GiB，不能直接开 4 个重任务再叠加构建开销。建议先 2 并发、构建并发 1～2，并按声明资源调度；更高并发依赖实测余量、宿主资源和服务端配额。

按“串行 30 小时”假设，完全无竞争时 2 并发的算术值为 15 小时、4 并发为 7.5 小时；实际受模型配额、重任务、构建和尾部任务制约。这些不是已验证交付承诺。并发主要减少墙钟时间，通常不会等比例减少 token 费用；减少无效重跑才能直接减少费用。

Docker 官方建议 WSL 下尽量从 Linux 文件系统提供容器文件。当前 C:\ 上的大型 node_modules 和 SQLite/log/workspace 热路径跨文件系统，值得优先移入镜像层及 Docker 本地卷，结束后再批量导出 Windows。只需小型进度状态持续对外可读，无需把所有热数据实时写到 C:\。[Docker WSL 最佳实践](https://docs.docker.com/desktop/features/wsl/best-practices/)

不建议把“单实例共享数据库和工作区跑全部题”、任意收紧题目超时、降低输出预算、换更小模型或隐藏失败作为主基线提速手段。若要探索这些配置，应单独命名 profile 并保留比较条件。

快速回归子集应覆盖已知风险：工具流式组装、/root 与非 /root、Skill 发现与资源读取、多根映射、长事件流、失败与取消。大多数 harness 风险用固定公共 API 事件 fixture 和独立 verifier fixture 即可验证，不需要每次消耗真实模型请求。复杂题与正式全量仍按原预算执行。

## 6. 下一轮完成标准

- 新 Linux 编译包作为单一显式输入，报告能够查到确切内容摘要及配置，不自动沿用历史补丁。
- 至少完成多类型小批量接入验证；with-skill 的发现与加载、路径输入输出、终态/取消和原 verifier 均有证据。
- 相同批次中断后只继续剩余有效任务；新产品/模型/profile 不复用旧批次结果。
- 所有 attempt、正式首次结果与诊断重跑可追溯，框架失败保留在端到端结果中。
- 报告的模型、耗时、CTRF、token 和失败原因来自可定位事实；未知数据明确留空或标未知。
- 用相同代表任务测量串行与 2 并发的阶段耗时、成功率、429 和资源峰值，再估算全量完成时间。

原包冒烟已发现的产品/依赖问题应进入正常 NextAgent 修复交付流程；评测基础设施的修复、版本化和验证留在评测工程，避免每次新包都重新通过聊天排查同一组基础问题。
