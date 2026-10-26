# 原全量评测结果整理

批次：`20261025-195147-f17d59ed-c79fa2`；状态：**STOPPED（人工结束）**。

- 计划 87 题；82 题已结束，3 题中断，2 题未启动。
- 39 题有有效数值评分，覆盖率 44.83%；其中 7 题 PASSED，32 题为有效失败或超时。
- 首次有效分数合计 7.6，已评分题均分 19.49%。覆盖不足，**没有完整 87 题总分**；不能把未评分题视作模型答错。
- 采用首次有效评分；保留原始 reward、所有历史 attempt 和环境/接入失败记录。

## 最新执行状态分布

| 最新状态 | 题数 |
|---|---:|
| ENVIRONMENT_ERROR | 39 |
| EXECUTION_FAILED | 14 |
| INTERRUPTED | 3 |
| NOT_STARTED | 2 |
| PASSED | 7 |
| PREFLIGHT_ERROR | 3 |
| TASK_FAILED | 10 |
| TIMEOUT | 8 |
| VERIFIER_ERROR | 1 |

`results.xlsx` 的“首次有效结果”在没有有效分数时展示首次 attempt，因此其无分题状态与这里的“最新执行状态”可能不同；两种口径都没有改分。

## 文件入口

- [原始 Excel 汇总](results.xlsx)：批次概览、首次有效结果、全部尝试。
- [原始结构化结果](results.json)；[现有 Markdown 报表](report.md)。
- 每题先看 `tasks/<task>/attempt-*/result.json`，再看 verifier 和实际轨迹。
- `nextagent-home.tar` 保存完整工作区与原生日志；`nextagent-home/logs/` 是日志的可读副本。
- `trajectory.jsonl` 为评测器接收的正式请求事件；模型 wire 证据在 `model-gateway/*/exchanges.tar`。
- `exports/20261026T031014814864Z/completed-framework-traces.ndjson` 是旧时点的合并快照，覆盖 36 个有原生日志的任务；**不包含后来完成的全部任务，也不是完整 Hook 边界轨迹**。
- 原批次排除了开发诊断 Hook；原生文件中的恢复事件不能替代缺失的调用边界。详见 `diagnostic-format-review/findings.json`。

## 失败与未完成题

软件源 502/连接失败、Docker Hub EOF、构建超时、欠费鉴权及框架/模型失败是不同类别。这里只按记录的 outcome/阶段归类，未把全部环境超时强行归因为网络。历史模型分析存在证据不足和未完成状态，不作为确定根因。

| 任务 | 最新状态 | 首次有效分数 | 失败阶段 | 结果入口 |
|---|---|---:|---|---|
| 3d-scan-calc | PASSED | 1 |  | [result.json](tasks/3d-scan-calc/attempt-001/result.json) |
| ada-bathroom-plan-repair | EXECUTION_FAILED | 0 |  | [result.json](tasks/ada-bathroom-plan-repair/attempt-002/result.json) |
| adaptive-cruise-control | EXECUTION_FAILED | 0 |  | [result.json](tasks/adaptive-cruise-control/attempt-001/result.json) |
| azure-bgp-oscillation-route-leak | EXECUTION_FAILED | 0 |  | [result.json](tasks/azure-bgp-oscillation-route-leak/attempt-001/result.json) |
| bike-rebalance | TIMEOUT | 0 |  | [result.json](tasks/bike-rebalance/attempt-001/result.json) |
| citation-check | ENVIRONMENT_ERROR |  | build | [result.json](tasks/citation-check/attempt-001/result.json) |
| civ6-adjacency-optimizer | TIMEOUT | 0 |  | [result.json](tasks/civ6-adjacency-optimizer/attempt-001/result.json) |
| court-form-filling | TASK_FAILED | 0 |  | [result.json](tasks/court-form-filling/attempt-001/result.json) |
| crystallographic-wyckoff-position-analysis | PASSED | 1 |  | [result.json](tasks/crystallographic-wyckoff-position-analysis/attempt-001/result.json) |
| dapt-intrusion-detection | ENVIRONMENT_ERROR |  | build | [result.json](tasks/dapt-intrusion-detection/attempt-001/result.json) |
| data-to-d3 | ENVIRONMENT_ERROR |  | build | [result.json](tasks/data-to-d3/attempt-001/result.json) |
| debug-trl-grpo | TASK_FAILED | 0.6 |  | [result.json](tasks/debug-trl-grpo/attempt-001/result.json) |
| dialogue-parser | EXECUTION_FAILED | 0 |  | [result.json](tasks/dialogue-parser/attempt-001/result.json) |
| drone-planning-control | TASK_FAILED | 0 |  | [result.json](tasks/drone-planning-control/attempt-001/result.json) |
| dynamic-object-aware-egomotion | EXECUTION_FAILED | 0 |  | [result.json](tasks/dynamic-object-aware-egomotion/attempt-001/result.json) |
| earthquake-phase-association | ENVIRONMENT_ERROR |  | build | [result.json](tasks/earthquake-phase-association/attempt-001/result.json) |
| earthquake-plate-calculation | TIMEOUT | 0 |  | [result.json](tasks/earthquake-plate-calculation/attempt-001/result.json) |
| econ-detrending-correlation | TASK_FAILED | 0 |  | [result.json](tasks/econ-detrending-correlation/attempt-001/result.json) |
| edit-pdf | EXECUTION_FAILED | 0 |  | [result.json](tasks/edit-pdf/attempt-001/result.json) |
| energy-ac-optimal-power-flow | TASK_FAILED | 0 |  | [result.json](tasks/energy-ac-optimal-power-flow/attempt-001/result.json) |
| energy-market-pricing | TIMEOUT | 0 |  | [result.json](tasks/energy-market-pricing/attempt-001/result.json) |
| energy-unit-commitment | TIMEOUT | 0 |  | [result.json](tasks/energy-unit-commitment/attempt-001/result.json) |
| enterprise-information-search | TASK_FAILED | 0 |  | [result.json](tasks/enterprise-information-search/attempt-001/result.json) |
| exam-block-sequencing | EXECUTION_FAILED | 0 |  | [result.json](tasks/exam-block-sequencing/attempt-001/result.json) |
| exceltable-in-ppt | ENVIRONMENT_ERROR |  | build | [result.json](tasks/exceltable-in-ppt/attempt-001/result.json) |
| exoplanet-detection-period | TASK_FAILED | 0 |  | [result.json](tasks/exoplanet-detection-period/attempt-001/result.json) |
| financial-modeling-qa | ENVIRONMENT_ERROR |  | build | [result.json](tasks/financial-modeling-qa/attempt-001/result.json) |
| fix-build-agentops | ENVIRONMENT_ERROR |  | build | [result.json](tasks/fix-build-agentops/attempt-001/result.json) |
| fix-build-google-auto | ENVIRONMENT_ERROR |  | build | [result.json](tasks/fix-build-google-auto/attempt-001/result.json) |
| fix-druid-loophole-cve | ENVIRONMENT_ERROR |  | queued | [result.json](tasks/fix-druid-loophole-cve/attempt-001/result.json) |
| fix-erlang-ssh-cve | ENVIRONMENT_ERROR |  | build | [result.json](tasks/fix-erlang-ssh-cve/attempt-001/result.json) |
| fix-visual-stability | ENVIRONMENT_ERROR |  | build | [result.json](tasks/fix-visual-stability/attempt-001/result.json) |
| flink-query | ENVIRONMENT_ERROR |  | build | [result.json](tasks/flink-query/attempt-001/result.json) |
| flood-risk-analysis | PASSED | 1 |  | [result.json](tasks/flood-risk-analysis/attempt-001/result.json) |
| glm-lake-mendota | TASK_FAILED | 0 |  | [result.json](tasks/glm-lake-mendota/attempt-001/result.json) |
| gravitational-wave-detection | PASSED | 1 |  | [result.json](tasks/gravitational-wave-detection/attempt-001/result.json) |
| grid-dispatch-operator | EXECUTION_FAILED | 0 |  | [result.json](tasks/grid-dispatch-operator/attempt-001/result.json) |
| hvac-control | PASSED | 1 |  | [result.json](tasks/hvac-control/attempt-001/result.json) |
| invoice-fraud-detection | PREFLIGHT_ERROR |  | workspace_preflight | [result.json](tasks/invoice-fraud-detection/attempt-001/result.json) |
| jax-computing-basics | EXECUTION_FAILED | 0 |  | [result.json](tasks/jax-computing-basics/attempt-001/result.json) |
| jpg-ocr-stat | PREFLIGHT_ERROR |  | workspace_preflight | [result.json](tasks/jpg-ocr-stat/attempt-001/result.json) |
| lab-unit-harmonization | ENVIRONMENT_ERROR |  | build | [result.json](tasks/lab-unit-harmonization/attempt-001/result.json) |
| lake-warming-attribution | PASSED | 1 |  | [result.json](tasks/lake-warming-attribution/attempt-002/result.json) |
| latex-formula-extraction | ENVIRONMENT_ERROR |  | build | [result.json](tasks/latex-formula-extraction/attempt-002/result.json) |
| lean4-proof | ENVIRONMENT_ERROR |  | build | [result.json](tasks/lean4-proof/attempt-001/result.json) |
| llm-prefix-cache-replay | PASSED | 1 |  | [result.json](tasks/llm-prefix-cache-replay/attempt-001/result.json) |
| manufacturing-codebook-normalization | TIMEOUT | 0 |  | [result.json](tasks/manufacturing-codebook-normalization/attempt-001/result.json) |
| manufacturing-equipment-maintenance | VERIFIER_ERROR |  |  | [result.json](tasks/manufacturing-equipment-maintenance/attempt-001/result.json) |
| manufacturing-fjsp-optimization | EXECUTION_FAILED | 0 |  | [result.json](tasks/manufacturing-fjsp-optimization/attempt-001/result.json) |
| mario-coin-counting | ENVIRONMENT_ERROR |  | build | [result.json](tasks/mario-coin-counting/attempt-001/result.json) |
| mars-clouds-clustering | EXECUTION_FAILED | 0 |  | [result.json](tasks/mars-clouds-clustering/attempt-001/result.json) |
| multilingual-video-dubbing | ENVIRONMENT_ERROR |  | build | [result.json](tasks/multilingual-video-dubbing/attempt-001/result.json) |
| offer-letter-generator | ENVIRONMENT_ERROR |  | build | [result.json](tasks/offer-letter-generator/attempt-001/result.json) |
| organize-messy-files | ENVIRONMENT_ERROR |  | build | [result.json](tasks/organize-messy-files/attempt-001/result.json) |
| paper-anonymizer | ENVIRONMENT_ERROR |  | build | [result.json](tasks/paper-anonymizer/attempt-001/result.json) |
| parallel-tfidf-search | PREFLIGHT_ERROR |  | workspace_preflight | [result.json](tasks/parallel-tfidf-search/attempt-001/result.json) |
| paratransit-routing | ENVIRONMENT_ERROR |  | build | [result.json](tasks/paratransit-routing/attempt-001/result.json) |
| pddl-airport-planning | ENVIRONMENT_ERROR |  | build | [result.json](tasks/pddl-airport-planning/attempt-001/result.json) |
| pddl-tpp-planning | ENVIRONMENT_ERROR |  | build | [result.json](tasks/pddl-tpp-planning/attempt-001/result.json) |
| pdf-excel-diff | ENVIRONMENT_ERROR |  | build | [result.json](tasks/pdf-excel-diff/attempt-001/result.json) |
| powerlifting-coef-calc | ENVIRONMENT_ERROR |  | build | [result.json](tasks/powerlifting-coef-calc/attempt-001/result.json) |
| pptx-reference-formatting | EXECUTION_FAILED | 0 |  | [result.json](tasks/pptx-reference-formatting/attempt-001/result.json) |
| protein-expression-analysis | ENVIRONMENT_ERROR |  | build | [result.json](tasks/protein-expression-analysis/attempt-001/result.json) |
| python-scala-translation | ENVIRONMENT_ERROR |  | build | [result.json](tasks/python-scala-translation/attempt-001/result.json) |
| quantum-numerical-simulation | EXECUTION_FAILED | 0 |  | [result.json](tasks/quantum-numerical-simulation/attempt-001/result.json) |
| r2r-mpc-control | EXECUTION_FAILED | 0 |  | [result.json](tasks/r2r-mpc-control/attempt-001/result.json) |
| radar-vital-signs | TIMEOUT | 0 |  | [result.json](tasks/radar-vital-signs/attempt-001/result.json) |
| react-performance-debugging | ENVIRONMENT_ERROR |  | build | [result.json](tasks/react-performance-debugging/attempt-001/result.json) |
| reserves-at-risk-calc | ENVIRONMENT_ERROR |  | build | [result.json](tasks/reserves-at-risk-calc/attempt-001/result.json) |
| sales-pivot-analysis | TASK_FAILED | 0 |  | [result.json](tasks/sales-pivot-analysis/attempt-001/result.json) |
| sec-financial-report | ENVIRONMENT_ERROR |  | build | [result.json](tasks/sec-financial-report/attempt-001/result.json) |
| seismic-phase-picking | ENVIRONMENT_ERROR |  | build | [result.json](tasks/seismic-phase-picking/attempt-001/result.json) |
| setup-fuzzing-py | TIMEOUT | 0 |  | [result.json](tasks/setup-fuzzing-py/attempt-001/result.json) |
| shock-analysis-demand | ENVIRONMENT_ERROR |  | build | [result.json](tasks/shock-analysis-demand/attempt-001/result.json) |
| shock-analysis-supply | ENVIRONMENT_ERROR |  | build | [result.json](tasks/shock-analysis-supply/attempt-001/result.json) |
| simpo-code-reproduction | TASK_FAILED | 0 |  | [result.json](tasks/simpo-code-reproduction/attempt-001/result.json) |
| software-dependency-audit | ENVIRONMENT_ERROR |  | build | [result.json](tasks/software-dependency-audit/attempt-001/result.json) |
| spring-boot-jakarta-migration | ENVIRONMENT_ERROR |  | build | [result.json](tasks/spring-boot-jakarta-migration/attempt-001/result.json) |
| suricata-custom-exfil | ENVIRONMENT_ERROR |  | build | [result.json](tasks/suricata-custom-exfil/attempt-001/result.json) |
| syzkaller-ppdev-syzlang | INTERRUPTED |  |  | [result.json](tasks/syzkaller-ppdev-syzlang/attempt-001/result.json) |
| threejs-structure-parser | ENVIRONMENT_ERROR |  | build | [result.json](tasks/threejs-structure-parser/attempt-001/result.json) |
| threejs-to-obj | ENVIRONMENT_ERROR |  | build | [result.json](tasks/threejs-to-obj/attempt-001/result.json) |
| tictoc-unnecessary-abort-detection | INTERRUPTED |  | bootstrap | [result.json](tasks/tictoc-unnecessary-abort-detection/attempt-001/result.json) |
| travel-planning | INTERRUPTED |  | bootstrap | [result.json](tasks/travel-planning/attempt-001/result.json) |
| video-silence-remover | ENVIRONMENT_ERROR |  | build | [result.json](tasks/video-silence-remover/attempt-001/result.json) |
| weighted-gdp-calc | NOT_STARTED |  |  | 未启动 |
| xlsx-recover-data | NOT_STARTED |  |  | 未启动 |

## 已批准的单独补测

仅 `ada-bathroom-plan-repair`、`azure-bgp-oscillation-route-leak` 已获本次人工批准，恢复开发诊断 Hook 后在独立批次执行。

- [补测配置与授权说明](../20261026-161356-f17d59ed-b0c82d/rerun-context.json)。
- [不调用模型的 Hook 启动验证](../20261026-161356-f17d59ed-b0c82d/validation/hook-startup/proof.json)。
- 框架工件、题库、模型、系统配置及 verifier/oracle 沿用；恢复六阶段 Hook，任务并发为 2。
- 原全量不继续，其他失败题不重跑；两题新分数不替代原首测分数。

## 清理状态

可再生构建缓存、孤立导入暂存和调试启动日志共约 898 MiB，清单在 [cleanup-manifest.json](cleanup-manifest.json)。
已逐项核验并删除上述临时文件，清理 941,876,472 字节（约 898.2 MiB）。原递归/强制删除命令被审批拒绝后，改用明确文件路径、无强制和无递归的逐项删除，再移除空目录；清单内目标已全部清除。
任务产物、原生轨迹、冻结配置、模型证据、框架/题库输入、凭据和运行依赖保留。

补测已经完成，结果见 [两题补测说明](../20261026-161356-f17d59ed-b0c82d/RERUN-SUMMARY.md)，原分数保持不变。
