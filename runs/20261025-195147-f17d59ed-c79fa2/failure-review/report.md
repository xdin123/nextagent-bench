# 历史评测失败原因汇总

仅分析现有证据，不调用模型、不重跑 Agent、不改评分。各批次分别统计，补测不替换原首测。

## 20261025-195147-f17d59ed-c79fa2

| 原因类别 | 数量 |
|---|---:|
| Agent 执行超时 (`AGENT_TIME_BUDGET_EXCEEDED`) | 8 |
| 软件源或依赖下载连接失败/502 (`APT_OR_DEPENDENCY_NETWORK`) | 16 |
| 构建超时；具体根因未证实 (`BUILD_TIMEOUT_CAUSE_UNPROVEN`) | 18 |
| 依赖下载 TLS/EOF/连接中断 (`DEPENDENCY_DOWNLOAD_TLS_OR_NETWORK`) | 3 |
| 题目内存声明超过 Docker 调度容量 (`DOCKER_MEMORY_CAPACITY`) | 1 |
| Docker 镜像仓库传输失败 (`DOCKER_REGISTRY_TRANSPORT`) | 1 |
| 框架与模型重复输出处理交互 (`FRAMEWORK_MODEL_DUPLICATION_INTERACTION`) | 7 |
| 框架或评测器异常，根因待查 (`FRAMEWORK_OR_HARNESS_UNRESOLVED`) | 2 |
| 评测器迁移 /tmp 丢失权限；已复现并修复 (`HARNESS_TMP_PERMISSION_REGRESSION`) | 1 |
| 执行中断；不记为模型答错 (`INTERRUPTED_NOT_MODEL_FAILURE`) | 3 |
| 模型账号鉴权/欠费影响 (`MODEL_ACCOUNT_AUTH_OR_BILLING`) | 3 |
| 模型服务或传输异常 (`MODEL_PROVIDER_OR_TRANSPORT`) | 3 |
| 模型返回协议/框架归一化问题待查 (`MODEL_RESPONSE_PROTOCOL_OR_NORMALIZATION`) | 1 |
| 未启动 (`NOT_EXECUTED`) | 2 |
| 验证通过 (`PASSED`) | 7 |
| 预检被中断；不能当作模型直接失败 (`PREFLIGHT_INTERRUPTED_NOT_DIRECT_MODEL_ERROR`) | 1 |
| 输出未满足原验证器断言 (`VERIFIER_ASSERTIONS_NOT_MET`) | 10 |

## 20261026-161356-f17d59ed-b0c82d

| 原因类别 | 数量 |
|---|---:|
| 框架与模型重复输出处理交互 (`FRAMEWORK_MODEL_DUPLICATION_INTERACTION`) | 2 |

## 逐题证据

重复输出属于框架检测与模型输出的交互现象，不能仅凭错误码判定单方责任；验证器断言失败和 Agent 超时也不自动归为 Docker 问题。

| 批次 | 任务 | 状态 | 分数 | 原因类别 | 可核验记录 |
|---|---|---|---:|---|---|
| 20261025-195147-f17d59ed-c79fa2 | ada-bathroom-plan-repair | EXECUTION_FAILED | 0 | FRAMEWORK_MODEL_DUPLICATION_INTERACTION | tasks/ada-bathroom-plan-repair/attempt-002/result.json |
| 20261025-195147-f17d59ed-c79fa2 | adaptive-cruise-control | EXECUTION_FAILED | 0 | MODEL_PROVIDER_OR_TRANSPORT | tasks/adaptive-cruise-control/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | azure-bgp-oscillation-route-leak | EXECUTION_FAILED | 0 | FRAMEWORK_MODEL_DUPLICATION_INTERACTION | tasks/azure-bgp-oscillation-route-leak/attempt-001/result.json; tasks/azure-bgp-oscillation-route-leak/attempt-001/verifier-stdout.txt:3; tasks/azure-bgp-oscillation-route-leak/attempt-001/verifier-stdout.txt:6 |
| 20261025-195147-f17d59ed-c79fa2 | bike-rebalance | TIMEOUT | 0 | AGENT_TIME_BUDGET_EXCEEDED | tasks/bike-rebalance/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | citation-check | ENVIRONMENT_ERROR |  | APT_OR_DEPENDENCY_NETWORK | tasks/citation-check/attempt-001/result.json; tasks/citation-check/attempt-001/environment-build.log:369; tasks/citation-check/attempt-001/environment-build.log:373 |
| 20261025-195147-f17d59ed-c79fa2 | civ6-adjacency-optimizer | TIMEOUT | 0 | AGENT_TIME_BUDGET_EXCEEDED | tasks/civ6-adjacency-optimizer/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | court-form-filling | TASK_FAILED | 0.0 | VERIFIER_ASSERTIONS_NOT_MET | tasks/court-form-filling/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | dapt-intrusion-detection | ENVIRONMENT_ERROR |  | APT_OR_DEPENDENCY_NETWORK | tasks/dapt-intrusion-detection/attempt-001/result.json; tasks/dapt-intrusion-detection/attempt-001/environment-build.log:165; tasks/dapt-intrusion-detection/attempt-001/environment-build.log:529 |
| 20261025-195147-f17d59ed-c79fa2 | data-to-d3 | ENVIRONMENT_ERROR |  | BUILD_TIMEOUT_CAUSE_UNPROVEN | tasks/data-to-d3/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | debug-trl-grpo | TASK_FAILED | 0.6 | VERIFIER_ASSERTIONS_NOT_MET | tasks/debug-trl-grpo/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | dialogue-parser | EXECUTION_FAILED | 0 | FRAMEWORK_MODEL_DUPLICATION_INTERACTION | tasks/dialogue-parser/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | drone-planning-control | TASK_FAILED | 0.0 | VERIFIER_ASSERTIONS_NOT_MET | tasks/drone-planning-control/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | dynamic-object-aware-egomotion | EXECUTION_FAILED | 0 | MODEL_RESPONSE_PROTOCOL_OR_NORMALIZATION | tasks/dynamic-object-aware-egomotion/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | earthquake-phase-association | ENVIRONMENT_ERROR |  | BUILD_TIMEOUT_CAUSE_UNPROVEN | tasks/earthquake-phase-association/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | earthquake-plate-calculation | TIMEOUT | 0 | AGENT_TIME_BUDGET_EXCEEDED | tasks/earthquake-plate-calculation/attempt-001/result.json; tasks/earthquake-plate-calculation/attempt-001/verifier-stdout.txt:3; tasks/earthquake-plate-calculation/attempt-001/verifier-stdout.txt:6 |
| 20261025-195147-f17d59ed-c79fa2 | econ-detrending-correlation | TASK_FAILED | 0.0 | VERIFIER_ASSERTIONS_NOT_MET | tasks/econ-detrending-correlation/attempt-001/result.json; tasks/econ-detrending-correlation/attempt-001/verifier-stdout.txt:3; tasks/econ-detrending-correlation/attempt-001/verifier-stdout.txt:6 |
| 20261025-195147-f17d59ed-c79fa2 | edit-pdf | EXECUTION_FAILED | 0 | FRAMEWORK_MODEL_DUPLICATION_INTERACTION | tasks/edit-pdf/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | energy-ac-optimal-power-flow | TASK_FAILED | 0.0 | VERIFIER_ASSERTIONS_NOT_MET | tasks/energy-ac-optimal-power-flow/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | energy-market-pricing | TIMEOUT | 0 | AGENT_TIME_BUDGET_EXCEEDED | tasks/energy-market-pricing/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | energy-unit-commitment | TIMEOUT | 0 | AGENT_TIME_BUDGET_EXCEEDED | tasks/energy-unit-commitment/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | enterprise-information-search | TASK_FAILED | 0.0 | VERIFIER_ASSERTIONS_NOT_MET | tasks/enterprise-information-search/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | exam-block-sequencing | EXECUTION_FAILED | 0 | FRAMEWORK_MODEL_DUPLICATION_INTERACTION | tasks/exam-block-sequencing/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | exceltable-in-ppt | ENVIRONMENT_ERROR |  | APT_OR_DEPENDENCY_NETWORK | tasks/exceltable-in-ppt/attempt-001/result.json; tasks/exceltable-in-ppt/attempt-001/environment-build.log:1578; tasks/exceltable-in-ppt/attempt-001/environment-build.log:1580 |
| 20261025-195147-f17d59ed-c79fa2 | exoplanet-detection-period | TASK_FAILED | 0.0 | VERIFIER_ASSERTIONS_NOT_MET | tasks/exoplanet-detection-period/attempt-001/result.json; tasks/exoplanet-detection-period/attempt-001/verifier-stdout.txt:3; tasks/exoplanet-detection-period/attempt-001/verifier-stdout.txt:6 |
| 20261025-195147-f17d59ed-c79fa2 | financial-modeling-qa | ENVIRONMENT_ERROR |  | APT_OR_DEPENDENCY_NETWORK | tasks/financial-modeling-qa/attempt-001/result.json; tasks/financial-modeling-qa/attempt-001/environment-build.log:483; tasks/financial-modeling-qa/attempt-001/environment-build.log:485 |
| 20261025-195147-f17d59ed-c79fa2 | fix-build-agentops | ENVIRONMENT_ERROR |  | BUILD_TIMEOUT_CAUSE_UNPROVEN | tasks/fix-build-agentops/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | fix-build-google-auto | ENVIRONMENT_ERROR |  | BUILD_TIMEOUT_CAUSE_UNPROVEN | tasks/fix-build-google-auto/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | fix-druid-loophole-cve | ENVIRONMENT_ERROR |  | DOCKER_MEMORY_CAPACITY | tasks/fix-druid-loophole-cve/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | fix-erlang-ssh-cve | ENVIRONMENT_ERROR |  | APT_OR_DEPENDENCY_NETWORK | tasks/fix-erlang-ssh-cve/attempt-001/result.json; tasks/fix-erlang-ssh-cve/attempt-001/environment-build.log:370; tasks/fix-erlang-ssh-cve/attempt-001/environment-build.log:372 |
| 20261025-195147-f17d59ed-c79fa2 | fix-visual-stability | ENVIRONMENT_ERROR |  | BUILD_TIMEOUT_CAUSE_UNPROVEN | tasks/fix-visual-stability/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | flink-query | ENVIRONMENT_ERROR |  | BUILD_TIMEOUT_CAUSE_UNPROVEN | tasks/flink-query/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | glm-lake-mendota | TASK_FAILED | 0.0 | VERIFIER_ASSERTIONS_NOT_MET | tasks/glm-lake-mendota/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | grid-dispatch-operator | EXECUTION_FAILED | 0 | MODEL_ACCOUNT_AUTH_OR_BILLING | tasks/grid-dispatch-operator/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | invoice-fraud-detection | PREFLIGHT_ERROR |  | PREFLIGHT_INTERRUPTED_NOT_DIRECT_MODEL_ERROR | tasks/invoice-fraud-detection/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | jax-computing-basics | EXECUTION_FAILED | 0 | MODEL_ACCOUNT_AUTH_OR_BILLING | tasks/jax-computing-basics/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | jpg-ocr-stat | PREFLIGHT_ERROR |  | MODEL_ACCOUNT_AUTH_OR_BILLING | tasks/jpg-ocr-stat/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | lab-unit-harmonization | ENVIRONMENT_ERROR |  | APT_OR_DEPENDENCY_NETWORK | tasks/lab-unit-harmonization/attempt-001/result.json; tasks/lab-unit-harmonization/attempt-001/environment-build.log:183; tasks/lab-unit-harmonization/attempt-001/environment-build.log:204 |
| 20261025-195147-f17d59ed-c79fa2 | latex-formula-extraction | ENVIRONMENT_ERROR |  | BUILD_TIMEOUT_CAUSE_UNPROVEN | tasks/latex-formula-extraction/attempt-002/result.json |
| 20261025-195147-f17d59ed-c79fa2 | lean4-proof | ENVIRONMENT_ERROR |  | BUILD_TIMEOUT_CAUSE_UNPROVEN | tasks/lean4-proof/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | manufacturing-codebook-normalization | TIMEOUT | 0 | AGENT_TIME_BUDGET_EXCEEDED | tasks/manufacturing-codebook-normalization/attempt-001/result.json; tasks/manufacturing-codebook-normalization/attempt-001/verifier-stdout.txt:3; tasks/manufacturing-codebook-normalization/attempt-001/verifier-stdout.txt:6 |
| 20261025-195147-f17d59ed-c79fa2 | manufacturing-equipment-maintenance | VERIFIER_ERROR |  | HARNESS_TMP_PERMISSION_REGRESSION | tasks/manufacturing-equipment-maintenance/attempt-001/result.json; maintenance/20261026-docker-repair/tmp-apt-validation/proof.json; tasks/manufacturing-equipment-maintenance/attempt-001/verifier-stdout.txt:3; tasks/manufacturing-equipment-maintenance/attempt-001/verifier-stdout.txt:6 |
| 20261025-195147-f17d59ed-c79fa2 | manufacturing-fjsp-optimization | EXECUTION_FAILED | 0 | FRAMEWORK_MODEL_DUPLICATION_INTERACTION | tasks/manufacturing-fjsp-optimization/attempt-001/result.json; tasks/manufacturing-fjsp-optimization/attempt-001/verifier-stdout.txt:3; tasks/manufacturing-fjsp-optimization/attempt-001/verifier-stdout.txt:6 |
| 20261025-195147-f17d59ed-c79fa2 | mario-coin-counting | ENVIRONMENT_ERROR |  | BUILD_TIMEOUT_CAUSE_UNPROVEN | tasks/mario-coin-counting/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | mars-clouds-clustering | EXECUTION_FAILED | 0 | FRAMEWORK_OR_HARNESS_UNRESOLVED | tasks/mars-clouds-clustering/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | multilingual-video-dubbing | ENVIRONMENT_ERROR |  | APT_OR_DEPENDENCY_NETWORK | tasks/multilingual-video-dubbing/attempt-001/result.json; tasks/multilingual-video-dubbing/attempt-001/environment-build.log:1182; tasks/multilingual-video-dubbing/attempt-001/environment-build.log:1184 |
| 20261025-195147-f17d59ed-c79fa2 | offer-letter-generator | ENVIRONMENT_ERROR |  | APT_OR_DEPENDENCY_NETWORK | tasks/offer-letter-generator/attempt-001/result.json; tasks/offer-letter-generator/attempt-001/environment-build.log:190; tasks/offer-letter-generator/attempt-001/environment-build.log:192 |
| 20261025-195147-f17d59ed-c79fa2 | organize-messy-files | ENVIRONMENT_ERROR |  | APT_OR_DEPENDENCY_NETWORK | tasks/organize-messy-files/attempt-001/result.json; tasks/organize-messy-files/attempt-001/environment-build.log:24; tasks/organize-messy-files/attempt-001/environment-build.log:26 |
| 20261025-195147-f17d59ed-c79fa2 | paper-anonymizer | ENVIRONMENT_ERROR |  | APT_OR_DEPENDENCY_NETWORK | tasks/paper-anonymizer/attempt-001/result.json; tasks/paper-anonymizer/attempt-001/environment-build.log:24; tasks/paper-anonymizer/attempt-001/environment-build.log:26 |
| 20261025-195147-f17d59ed-c79fa2 | parallel-tfidf-search | PREFLIGHT_ERROR |  | MODEL_PROVIDER_OR_TRANSPORT | tasks/parallel-tfidf-search/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | paratransit-routing | ENVIRONMENT_ERROR |  | DEPENDENCY_DOWNLOAD_TLS_OR_NETWORK | tasks/paratransit-routing/attempt-001/result.json; tasks/paratransit-routing/attempt-001/environment-build.log:26; tasks/paratransit-routing/attempt-001/environment-build.log:27 |
| 20261025-195147-f17d59ed-c79fa2 | pddl-airport-planning | ENVIRONMENT_ERROR |  | DEPENDENCY_DOWNLOAD_TLS_OR_NETWORK | tasks/pddl-airport-planning/attempt-001/result.json; tasks/pddl-airport-planning/attempt-001/environment-build.log:29; tasks/pddl-airport-planning/attempt-001/environment-build.log:30 |
| 20261025-195147-f17d59ed-c79fa2 | pddl-tpp-planning | ENVIRONMENT_ERROR |  | DEPENDENCY_DOWNLOAD_TLS_OR_NETWORK | tasks/pddl-tpp-planning/attempt-001/result.json; tasks/pddl-tpp-planning/attempt-001/environment-build.log:29; tasks/pddl-tpp-planning/attempt-001/environment-build.log:34 |
| 20261025-195147-f17d59ed-c79fa2 | pdf-excel-diff | ENVIRONMENT_ERROR |  | BUILD_TIMEOUT_CAUSE_UNPROVEN | tasks/pdf-excel-diff/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | powerlifting-coef-calc | ENVIRONMENT_ERROR |  | BUILD_TIMEOUT_CAUSE_UNPROVEN | tasks/powerlifting-coef-calc/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | pptx-reference-formatting | EXECUTION_FAILED | 0 | FRAMEWORK_MODEL_DUPLICATION_INTERACTION | tasks/pptx-reference-formatting/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | protein-expression-analysis | ENVIRONMENT_ERROR |  | BUILD_TIMEOUT_CAUSE_UNPROVEN | tasks/protein-expression-analysis/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | python-scala-translation | ENVIRONMENT_ERROR |  | BUILD_TIMEOUT_CAUSE_UNPROVEN | tasks/python-scala-translation/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | quantum-numerical-simulation | EXECUTION_FAILED | 0 | FRAMEWORK_OR_HARNESS_UNRESOLVED | tasks/quantum-numerical-simulation/attempt-001/result.json; tasks/quantum-numerical-simulation/attempt-001/verifier-stdout.txt:2; tasks/quantum-numerical-simulation/attempt-001/verifier-stdout.txt:5 |
| 20261025-195147-f17d59ed-c79fa2 | r2r-mpc-control | EXECUTION_FAILED | 0 | MODEL_PROVIDER_OR_TRANSPORT | tasks/r2r-mpc-control/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | radar-vital-signs | TIMEOUT | 0 | AGENT_TIME_BUDGET_EXCEEDED | tasks/radar-vital-signs/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | react-performance-debugging | ENVIRONMENT_ERROR |  | BUILD_TIMEOUT_CAUSE_UNPROVEN | tasks/react-performance-debugging/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | reserves-at-risk-calc | ENVIRONMENT_ERROR |  | BUILD_TIMEOUT_CAUSE_UNPROVEN | tasks/reserves-at-risk-calc/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | sales-pivot-analysis | TASK_FAILED | 0.0 | VERIFIER_ASSERTIONS_NOT_MET | tasks/sales-pivot-analysis/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | sec-financial-report | ENVIRONMENT_ERROR |  | BUILD_TIMEOUT_CAUSE_UNPROVEN | tasks/sec-financial-report/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | seismic-phase-picking | ENVIRONMENT_ERROR |  | BUILD_TIMEOUT_CAUSE_UNPROVEN | tasks/seismic-phase-picking/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | setup-fuzzing-py | TIMEOUT | 0 | AGENT_TIME_BUDGET_EXCEEDED | tasks/setup-fuzzing-py/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | shock-analysis-demand | ENVIRONMENT_ERROR |  | APT_OR_DEPENDENCY_NETWORK | tasks/shock-analysis-demand/attempt-001/result.json; tasks/shock-analysis-demand/attempt-001/environment-build.log:463; tasks/shock-analysis-demand/attempt-001/environment-build.log:486 |
| 20261025-195147-f17d59ed-c79fa2 | shock-analysis-supply | ENVIRONMENT_ERROR |  | APT_OR_DEPENDENCY_NETWORK | tasks/shock-analysis-supply/attempt-001/result.json; tasks/shock-analysis-supply/attempt-001/environment-build.log:25; tasks/shock-analysis-supply/attempt-001/environment-build.log:60 |
| 20261025-195147-f17d59ed-c79fa2 | simpo-code-reproduction | TASK_FAILED | 0.0 | VERIFIER_ASSERTIONS_NOT_MET | tasks/simpo-code-reproduction/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | software-dependency-audit | ENVIRONMENT_ERROR |  | APT_OR_DEPENDENCY_NETWORK | tasks/software-dependency-audit/attempt-001/result.json; tasks/software-dependency-audit/attempt-001/environment-build.log:24; tasks/software-dependency-audit/attempt-001/environment-build.log:27 |
| 20261025-195147-f17d59ed-c79fa2 | spring-boot-jakarta-migration | ENVIRONMENT_ERROR |  | APT_OR_DEPENDENCY_NETWORK | tasks/spring-boot-jakarta-migration/attempt-001/result.json; tasks/spring-boot-jakarta-migration/attempt-001/environment-build.log:24; tasks/spring-boot-jakarta-migration/attempt-001/environment-build.log:27 |
| 20261025-195147-f17d59ed-c79fa2 | suricata-custom-exfil | ENVIRONMENT_ERROR |  | DOCKER_REGISTRY_TRANSPORT | tasks/suricata-custom-exfil/attempt-001/result.json; tasks/suricata-custom-exfil/attempt-001/environment-build.log:8; tasks/suricata-custom-exfil/attempt-001/environment-build.log:18 |
| 20261025-195147-f17d59ed-c79fa2 | syzkaller-ppdev-syzlang | INTERRUPTED |  | INTERRUPTED_NOT_MODEL_FAILURE | tasks/syzkaller-ppdev-syzlang/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | threejs-structure-parser | ENVIRONMENT_ERROR |  | APT_OR_DEPENDENCY_NETWORK | tasks/threejs-structure-parser/attempt-001/result.json; tasks/threejs-structure-parser/attempt-001/environment-build.log:25; tasks/threejs-structure-parser/attempt-001/environment-build.log:29 |
| 20261025-195147-f17d59ed-c79fa2 | threejs-to-obj | ENVIRONMENT_ERROR |  | APT_OR_DEPENDENCY_NETWORK | tasks/threejs-to-obj/attempt-001/result.json; tasks/threejs-to-obj/attempt-001/environment-build.log:27; tasks/threejs-to-obj/attempt-001/environment-build.log:30 |
| 20261025-195147-f17d59ed-c79fa2 | tictoc-unnecessary-abort-detection | INTERRUPTED |  | INTERRUPTED_NOT_MODEL_FAILURE | tasks/tictoc-unnecessary-abort-detection/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | travel-planning | INTERRUPTED |  | INTERRUPTED_NOT_MODEL_FAILURE | tasks/travel-planning/attempt-001/result.json; tasks/travel-planning/attempt-001/environment-build.log:26; tasks/travel-planning/attempt-001/environment-build.log:27 |
| 20261025-195147-f17d59ed-c79fa2 | video-silence-remover | ENVIRONMENT_ERROR |  | BUILD_TIMEOUT_CAUSE_UNPROVEN | tasks/video-silence-remover/attempt-001/result.json |
| 20261025-195147-f17d59ed-c79fa2 | weighted-gdp-calc | NOT_STARTED |  | NOT_EXECUTED |  |
| 20261025-195147-f17d59ed-c79fa2 | xlsx-recover-data | NOT_STARTED |  | NOT_EXECUTED |  |
| 20261026-161356-f17d59ed-b0c82d | ada-bathroom-plan-repair | EXECUTION_FAILED | 0 | FRAMEWORK_MODEL_DUPLICATION_INTERACTION | tasks/ada-bathroom-plan-repair/attempt-001/result.json |
| 20261026-161356-f17d59ed-b0c82d | azure-bgp-oscillation-route-leak | EXECUTION_FAILED | 0 | FRAMEWORK_MODEL_DUPLICATION_INTERACTION | tasks/azure-bgp-oscillation-route-leak/attempt-001/result.json; tasks/azure-bgp-oscillation-route-leak/attempt-001/verifier-stdout.txt:3; tasks/azure-bgp-oscillation-route-leak/attempt-001/verifier-stdout.txt:6 |

带行号的简短错误证据、失败测试名、时限和归因置信范围见 summary.json。完整 prompt、reasoning 和轨迹正文不写入此汇总。
