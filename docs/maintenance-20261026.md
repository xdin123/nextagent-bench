# 2026-10-26 评测工程维护

## 授权与边界

用户要求下次评测按两份配置保留开发诊断 Hook，汇总历史失败并修复 Docker 环境问题。用户进一步明确不需要额外的 Hook 启动校验。因此只移除评测器的 Hook 过滤，不增加自动绑定、强制启用或新预检流程。框架产品、模型、冻结题库、任务语义和评分器不修改；本次没有新增 Agent 补测。

## 已修改

- `settings.py` 不再接收或执行 Hook 排除列表；`profiles/default-system.yaml` 的插件声明和 `profiles/agent.yaml` 的 Hook 绑定完整保留。旧排除字段不再影响生效配置。
- 路径桥接保留原目录的属主、属组和权限位。历史 `manufacturing-equipment-maintenance` 归档中，迁移后的 temp 为 `0755`，而系统 `/tmp` 应保持其原有 `1777`；此回归使 `_apt` 用户无法创建验签临时文件。修复不放宽其他目录，只保留其迁移前属性。
- 命令超时清理本命令拥有的进程树，避免只结束 docker.exe 而遗留 docker-buildx.exe。Windows 使用指定 PID 的 taskkill /T，POSIX 使用本命令独立进程组；不按进程名杀其他任务。
- 仅对 Docker 构建中有明确瞬时网络证据的失败最多尝试三次，全部共用原有构建时限；超时、Dockerfile 错误或依赖规格错误不重新获得时限。保留每次日志和 `.attempts.json`。此重试发生在调用 Agent 之前，不重跑已结束评测。
- 普通容器启动不再等候无关任务的镜像构建锁；Compose 启动可能构建辅助镜像，仍使用同一构建锁。任务并发及原有内存预约保持生效。排队后重新检查 STOP，避免人工停止后继续开始构建。
- `scripts/summarize_failures.py` 根据原始状态、终态码和带行号日志汇总历史失败，不调用分析模型，不把纯超时或普通 libssl 包名当作已证实网络故障。

## 验证

65 项测试全部通过，包含 8 项真实 Docker 契约测试。新增回归先复现了 Hook 被过滤、`/tmp` 变成 0755 和命令超时遗留子进程的问题；进程测试同时确认无关进程仍存活。调度测试验证一个已就绪普通容器不会被另一个构建阻塞，Compose 辅助构建仍保持预约。

在 `manufacturing-equipment-maintenance` 的全新容器中使用修复后的桥接，`/tmp` 为 1777，`apt-get update` 返回 0，没有 Permission denied；没有运行 Agent 或原 verifier。

历史失败环境 `threejs-to-obj` 与 `paratransit-routing` 独立环境构建验证均已成功，使用原 Dockerfile 和依赖版本，记录镜像 ID 和冻结文件摘要。日志和结果在 `runs/20261025-195147-f17d59ed-c79fa2/maintenance/20261026-docker-repair/environment-validation.json`；这不是新评测结果，也不表示所有历史构建超时都已重建或证实根因。

## 历史结果入口与未决项

逐题原因、证据文件/行号、置信范围见原全量批次 `failure-review/report.md` 和 `summary.json`，补测批次分列统计，不替换原分数。

原全量有 20 题留下明确依赖/软件源或镜像仓库连接失败证据，18 题只证明构建超时，不能把它们全部确定为同一网络根因。另有 1 题验证器受到上述 /tmp 回归影响。模型鉴权/欠费、模型传输、重复输出、协议、任务断言和 Agent 超时分别列出，不当作 Docker 缺陷。

`fix-druid-loophole-cve` 声明 16384 MiB；调整前 Docker 总内存约 15.46 GiB、80% 调度预算约 12.37 GiB，无法接纳。用户随后明确批准 WSL2 22 GiB 上限及 Docker/WSL 重启，已实施。Docker 实际可见 21.5 GiB，调度预算 17612 MiB（约17.2 GiB），16 GiB预约和实际容器启动均验证通过；未启动该题 Agent 补测。证据见同维护目录 `memory-change-validation.json`。重启后未观察到此前预构建的项目镜像标签；没有重启前即时清单，不能确定缺失发生时间或原因。本次未执行镜像清理或重置，原始评测结果摘要未变；后续缺失镜像会按冻结输入正常重建。

历史批次仍保留其原执行源码、配置和结果；本次代码只用于后续新批次。没有伪造旧适配器摘要或改写恢复校验记录。
