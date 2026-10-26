# 交付状态

独立项目：C:\Project\nextagent-bench。已有评测工程和 NextAgent 源码没有被修改，旧后台任务没有被停止。

用户目标：新 Linux 编译包可直接启动 SkillsBench；保留两配置、路径适配和完整产物；多个 key 共用账号配额；失败要做细粒度、多方、带证据的因果分析。

已实现：发行包/题库内容寻址导入，Docker 层缓存，真实 WORKDIR 多根桥接，启动前 Skill 注入及实际发现/调用/加载证据，配置隔离与有效值核对，分页轨迹，清洁 attempt，恢复/停止，原 verifier 与端到端分数分别保留，JSON/CSV/Excel 报告，私有 Docker 模型代理，共享额度/冷却/密钥隔离，16 维故障分析及 wire→normalized→input→feedback 逐调用联结。

凭据：DPAPI .secrets/keys/default.xml 和 shared-01 至 shared-04，共 5 个不同值。新四个来自用户2026-10-25本轮消息；只保存加密值，不复述。当前启用总并发1；未知 RPM/TPM 不虚构。未来脚本自动加载全部别名并去重。

验证：51 项不同用例（44 离线、本地 HTTP +7 Docker）已通过；Python/Node/PowerShell/pip 检查通过；源码和运行归档的已登记 key 扫描未发现泄漏。详见 VALIDATION.md。

真实运行：20261025-160051-f17d59ed-95ceb2 的3d-scan-calc通过，101.765秒，原verifier和e2e均1；代理集成后的20261025-165143-f17d59ed-909845 同题失败，214.750秒，原verifier和e2e均0，保留原样，未重跑到成功。后者已有材料完成单独的中文详细分析及一次格式修复，报告位于 analysis/20261025-171200-format/report.md；确定性核对标 REVIEW_REQUIRED，明确指出 sandbox 失败与模型环境正常结论的冲突，latest.json 为分析权威状态。失败观察与限制见验证记录，不把HTTP200/缺finish/SANDBOX_UNAVAILABLE简单混为单一根因。

原始bundle f84a... 与既有修补基线 f17d... 分开存放。默认使用既有授权基线，换新包不套补丁。87题离线路径计划成功，但未真实跑完87题，不宣称全量结果或固定加速倍数。

临时目录 artifacts/import-tgngqnt0 清理被自动审批 blocked by policy 拦截，已保留，不用于运行。不再尝试绕过审批清理。

使用入口 README.md / Start-Evaluation.ps1 / Set-ModelCredential.ps1 / Analyze-Failures.ps1。没有创建远端仓库、commit或push。


后续单题冒烟完成：runs/20261025-193448-f17d59ed-363fec，3d-scan-calc PASSED，e2e/reward均1，375.281秒，Agent340.735秒；mesh-analysis实际调用并加载，完整归档无错误，5个key轮换均HTTP200。此前172352批次暴露代理响应前断连不返回明确HTTP错误，已中止归档，先复现再修复并通过6项代理测试。详细见SMOKE-20261025.md。当前有效任务并发1，尚未真实验收两题并行，未执行87题全量。


全量批次195147-c79fa2：3d-scan-calc已通过，用户授权同批次2→3→4逐级调节并仅增量跑。已实现运行时调度/代理预算控制，目标2已生效；原完成结果哈希不变。当前runtime_adapter_sha=4f5d50753f4f23abc988562533a0deb321ea508210f2a493c734457a39d64064，原始adapter_sha仍保留c061...；adapter-upgrade.json及adapter-upgrades对应新源码快照已登记。当前runner日志launches/20261025-200449-0831.stdout.log。勿修改.py/.mjs后绕过恢复检查；后续调并发只用Set-Concurrency.ps1，不须重启。监控nextagent已改每15分钟，至少每档30分钟+2有效完成题+20请求，无配额/资源异常才升档，上限4，观察基线ramp-observations.json。当前ADA/ACC冷构建中，构建门仍串行，需观察之后两题实际模型执行。

