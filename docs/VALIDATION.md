# 验证记录 — 2026-10-25

这是实际执行范围；87 道题尚未全量执行。旧工程后台保持运行，新工程没有修改旧驱动、题库、框架源目录或 NextAgent 产品代码。

## 环境与基线

- 独立项目：`C:\Project\nextagent-bench`，Python 3.12.10；Docker Desktop Linux Engine。
- 现有已授权修补后的目录以不可变 tar 快照导入，SHA `f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5`。本项目没有再给产品打补丁。
- 原始发行 tar 也独立导入，SHA `f84a17e05c5ebbfc44a7595902abe9251bf8c0ad6cb62fdecd7753e02911b631`，SDK 2.0.62 保持原状；仅验证导入，没有宣称这个原包可以完成真实工具调用。导入实测 3.844 秒。
- 题库为现有已适配数据的冻结副本：SHA `c44fb04745607db4d1c0b07a945ec3fbdfaa2bd955ae172667aaa7edc95b4ae2`，87 道题、232 个 Skill 目录。
- 两份配置模板来自用户修改后的解压目录；运行所需的路径/端口/hook 差异有独立记录。真实 bootstrap 核对 `guardrail.enabled=false`。
- 现有 key 保存为本机 DPAPI 加密的 `default`；用户新提供的 4 个不同 key 已保存为 `shared-01` 至 `shared-04`，池中共 5 个不同值。后续真实单题冒烟已轮换使用全部 5 个 key，均取得 HTTP 200；共享限额并发行为另用两个测试 key 和本地受控服务验证，未进行真实限额压力测试。详见 [本次单题冒烟](SMOKE-20261025.md)。

## 自动检查

新增运行时并发测试后，44 项离线/本地 HTTP 测试通过；另行运行的 7 项 Docker 测试仍适用，共覆盖 51 项不同用例。

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
$env:NAB_DOCKER_TESTS = '1'
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_docker_integration.py -v
Remove-Item Env:\NAB_DOCKER_TESTS
```

主要验证面：

- 嵌套 YAML 预算、两配置保留与显式覆盖；多阶段最终 WORKDIR、多根文件互不覆盖、URL 不替换、系统根拒绝。
- Docker 中的真实路径桥接与原 verifier 路径可见性；Skill 不多套一层目录；system-local 注册事实与 Web user-invocable 列表区别。
- import-only ESM public export 可启动；超过 1000 条事件分页与去重；STOP 信号；POSIX tar 的 workspace、链接与日志保留。
- 原始 CTRF status、缺 reward 的错误分类、首次有效失败不被后续成功替换、冻结配置被改后拒绝混合恢复。
- 两个 key 共用一个并发和一个 429 冷却窗口；失效 key 隔离；请求体/SSE 字节保持；已开始的断流不重放；日志及 wire 证据无认证信息和 provider reasoning。
- 原始工具参数分片（含空 ID 续片）重组、JSON 与可见 schema 校验、按 ID 对照 normalized/input/下一轮反馈；伪造证据拒绝、维度覆盖、无因果重放时整体结论最多是假设；分析失败保留 score 与证据。
- 重复流不能挤掉指令/代码/反馈；传输 EOF 与 provider finish/DONE 区分；不同批次不得各自占用同一项目共享额度；报告格式修复最多一次，成功和失败都保留材料，且不改变 Agent 结果。

Python 编译、两份 `.mjs` 的 Node 语法检查、9 份 PowerShell 脚本解析、`pip check` 均通过。已对项目源码和已有运行归档检查了当前登记的 5 个真实 key，475 个文件/归档成员的检查未发现泄漏；不输出 key 内容。

全部 87 题的离线路径计划成功生成，约 7 秒。这仅证明适配计划可生成；不代表所有实际容器、依赖、路径动态构造及 verifier 都已真实验证。

## 真实 NextAgent / SkillsBench 运行

| 批次 | 实际结果 | 耗时与意义 |
|---|---|---|
| `20261025-154059-f17d59ed-4d419e` | 接入失败 | 首次冷构建约 308 秒；暴露 launcher 不支持 import-only export，已修复并保留失败材料 |
| `20261025-155611-f17d59ed-408514` | 接入检查误判 | bootstrap 约 5.8 秒，Skill 实际已注册；暴露把 Web 目录当作全部模型 Skills 的检查缺陷，已修复 |
| `20261025-160051-f17d59ed-95ceb2` | `3d-scan-calc` PASSED，score=1，原 verifier reward=1 | 总计 101.765 秒；Agent 68.641 秒；Skill 实际调用并成功加载；完整产物无采集错误。这次在共享代理接入前执行 |
| `20261025-165143-f17d59ed-909845` | `3d-scan-calc` EXECUTION_FAILED，score=0，原 verifier reward=0 | 经真实共享代理执行，总计 214.750 秒；Agent 173.344 秒；完整留证并触发失败分析，不重跑到成功 |
| `20261025-172352-f17d59ed-43ba88` | INTERRUPTED | 暴露代理在响应前断连时没有返回明确错误的问题，主动中止并保留；增加回归测试后修复 |
| `20261025-193448-f17d59ed-363fec` | `3d-scan-calc` PASSED，score=1，原 verifier reward=1 | 修复后以新批次/新容器完成单题；375.281 秒，准备约25秒，Agent340.735秒，全部5个key实际接入 |

新代理运行的细分耗时：缓存镜像 1.313 秒、容器准备 1.812 秒、启动 7.985 秒、Skill 检查 0.453 秒、scope priming 15.312 秒、停止 0.406 秒、原 verifier 12.500 秒、采集 1.610 秒。请求 `-Jobs 2` 时明确提示共享配额实际并发为 1。

新代理真实运行确认：mesh-analysis 已发现、调用、成功加载；采集了 12 次模型交换（包括独立 priming），正式请求的 10 次工具调用均通过模型可见 schema 校验。Python 工具返回 `SANDBOX_UNAVAILABLE/PYTHON_EXECUTION_UNAVAILABLE`。最后一轮终态为 `MODEL_RESPONSE_INVALID`，留存分片缺少 finish_reason / DONE。已完成代理记录都是 HTTP 200，不能据此把任务失败归为 429。

一处 Bash 参数在 wire 与诊断投影中有字符差异，但日志自身也可能做脱敏/投影；目前只作为需定位的观察，不宣称已证明运行时参数损坏。没有执行因果重放，因此不能把上面几项观察直接合并成已证实的单一根因。

两次同题结果不同，说明单题一次通过不能证明框架/模型组合稳定；上述耗时也不能外推为 87 题的固定加速倍数。prep 的缓存收益与模型实际推理时延分别记录。

## 失败分析验证

真实失败批次保留全部源证据、冻结适配器源码、对应发行包代码片段、tool-boundary-checks.json，以及每个分析版本的 packet/prompt/模型回复/错误状态。第一次模型回复完成了 16 维检查，但使用了 `INSUFFICIENT_EVIDENCE` 作为因果置信度，严格校验将其标为分析未完成；原文和错误均保留。现已把这个与 UNKNOWN 同义的不足证据值规范化，并保留原值；不会把弱结论提升为已证实。

发现初版提示被重复流分片占满后，已增加按证据种类轮流选取和定向指令投影。重做分析只读取同一批次现有材料，不重跑 Agent、不改变 score/reward。对第二次已保存模型回复进行一次格式转换后，完成了结构和证据引用校验，中文报告保存在 `runs/20261025-165143-f17d59ed-909845/tasks/3d-scan-calc/attempt-001/analysis/20261025-171200-format/report.md`。

人工抽查发现模型把专用 Python 工具的 sandbox 不可用误写成环境正常，并把部分日志参数差异说成全部一致。因此新增确定性事实核对，真实报告开头列出 sandbox 失败与记录值差异，并标 `audit_status=REVIEW_REQUIRED`；42 项用例中包括该冲突的回归验证。`SEMANTIC_ANALYSIS_COMPLETE` 只表示报告结构/维度/引用已完整，不表示因果结论已经证实。当前整体归因仍为有证据支持的候选假设，具体模型服务、代理、SDK 或框架责任需重放核验。没有把模型原始错误回复隐藏或改成事实。

最终分析状态和报告位置以本批次 `tasks/3d-scan-calc/attempt-001/analysis/latest.json` 为准；语义结论仍需人工核验。

## 保留的限制

- 未知账号 RPM/TPM 尚未填写，默认起步共享并发已按用户授权改为 2，当前批次可受控逐级升至 4。多个 key 不增加总额度；旧工程及外部客户端的用量不受本项目的锁控制。
- 没有声称 Docker Desktop 提供逐容器磁盘硬配额；只记录题目声明，CPU/内存已执行限制。
- 语义分析有独立调用和耗时，可能超时或输出不足；失败会保留材料并标状态。必要时先只留证，之后单独分析。
- 历史已中断导入目录 `artifacts/import-tgngqnt0` 没有被用于评测；清理动作被自动审批返回 `blocked by policy` 拦截，目录保留。
- 旧 BenchFlow 0.6.3 的 session-factory 声明与实际 ACP 执行链未贯通；本项目使用已验证 HTTP 入口的小型 runner。没有修改 BenchFlow 内部实现。


## 全量批次增量调整并发

批次20261025-195147-f17d59ed-c79fa2 首题3d-scan-calc已通过，278.094秒。按用户授权，待其结束再升级静态调度器；后续ADA attempt-001在任何模型执行前中断（0.094秒）并保留，当前ADA attempt-002和ACC attempt-001按2并发准备环境。原完成结果摘要核对未变，未新建批次，剩余86题增量继续。

运行时控制已通过真实Docker内控制接口将共享预算设为2；当前并发目标及应用状态分别在concurrency.json/concurrency-applied.json。新增测试覆盖热升档、降档不取消在途请求、drain、增量跳过全部完成结果、冻结输入仍不可变、升级源码快照匹配，以及Agent凭据无权改共享控制。两道题均完成的真实并发验收仍在进行，不能以控制设置和单元测试代替已完成的两题结果。

