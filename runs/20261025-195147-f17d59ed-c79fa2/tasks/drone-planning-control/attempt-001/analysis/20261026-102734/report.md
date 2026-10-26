# 分析未完成，需要核验

Diagnostic request failed: HTTP_502

Evidence packet retained where available; no unsupported root cause asserted. Retry diagnostics without rerunning the task.

原始回复见本目录 model-response.json / format-repair-response.json；不可把格式未验证的内容当作已证实根因。

## 已保存证据

- E001 / observed_result: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\result.json
- E002 / effective_task: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\agent-facing\prompt.txt
- E003 / path_and_skill_plan: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\agent-facing\adaptation.json
- E004 / physical_path_evidence: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\path-bridge.json
- E005 / effective_runtime_configuration: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\bootstrap.json
- E006 / skill_discovery: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\skill-discovery.json
- E007 / verifier_assertions: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\ctrf.json
- E008 / verifier_output: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\verifier-stdout.txt
- E009 / startup_evidence: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\runtime\na-start.log
- E010 / provided_skill_document: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\agent-facing\skills\attitude-controller-planner\SKILL.md
- E011 / provided_skill_document: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\agent-facing\skills\flight-plan-parser\SKILL.md
- E012 / provided_skill_document: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\agent-facing\skills\motor-model-dynamics\SKILL.md
- E013 / frozen_configuration: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\config\default-system.yaml
- E014 / frozen_configuration: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\config\agent.yaml
- E015 / frozen_configuration: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\config\changes.json
- E016 / frozen_configuration: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\config\quota.json
- E017 / canonical_execution_timeline: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\trajectory.jsonl
- E018 / framework_model_and_tool_boundaries: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home\logs
- E019 / actual_model_request: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/drone-planning-control/attempt-1/ab169864a9264a4ba750e1ee561e38f7/request.json
- E020 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/drone-planning-control/attempt-1/ab169864a9264a4ba750e1ee561e38f7/request.json
- E021 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/drone-planning-control/attempt-1/ab169864a9264a4ba750e1ee561e38f7/
- E022 / actual_model_request: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/drone-planning-control/attempt-1/59c395d95b484d58b49e1965f2466a95/request.json
- E023 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/drone-planning-control/attempt-1/59c395d95b484d58b49e1965f2466a95/request.json
- E024 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/drone-planning-control/attempt-1/59c395d95b484d58b49e1965f2466a95/
- E025 / actual_model_request: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/drone-planning-control/attempt-1/d715ec146fd04dcb8d860ae06cc82b2b/request.json
- E026 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/drone-planning-control/attempt-1/d715ec146fd04dcb8d860ae06cc82b2b/request.json
- E027 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/drone-planning-control/attempt-1/d715ec146fd04dcb8d860ae06cc82b2b/
- E028 / actual_model_request: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/drone-planning-control/attempt-1/3d1556383dec46358d0a733a527cf32b/request.json
- E029 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/drone-planning-control/attempt-1/3d1556383dec46358d0a733a527cf32b/request.json
- E030 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/drone-planning-control/attempt-1/3d1556383dec46358d0a733a527cf32b/
- E031 / actual_model_request: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/drone-planning-control/attempt-1/4279845bb1514ea188c4dedf426fbdb7/request.json
- E032 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/drone-planning-control/attempt-1/4279845bb1514ea188c4dedf426fbdb7/request.json
- E033 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/drone-planning-control/attempt-1/4279845bb1514ea188c4dedf426fbdb7/
- E034 / actual_model_request: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/drone-planning-control/attempt-1/0ee0eb7c7f7d471b84f3f82afc1e068d/request.json
- E035 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/drone-planning-control/attempt-1/0ee0eb7c7f7d471b84f3f82afc1e068d/request.json
- E036 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/drone-planning-control/attempt-1/0ee0eb7c7f7d471b84f3f82afc1e068d/
- E037 / joined_tool_boundaries: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\tool-boundary-checks.json
- E038 / frozen_harness_code: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\adapter-upgrades\4f5d50753f4f23abc988562533a0deb321ea508210f2a493c734457a39d64064\source\runtime\helper.mjs
- E039 / frozen_harness_code: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\adapter-upgrades\4f5d50753f4f23abc988562533a0deb321ea508210f2a493c734457a39d64064\source\runtime\start.mjs
- E040 / operator_concurrency_history: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\concurrency-history.jsonl
- E041 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-core/dist/tools/skill-catalog-query-port.js
- E042 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-capability/dist/skills/skill-manifest.js
- E043 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-capability/dist/local/skill-discovery.js
- E044 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-platform-gateway-local/dist/sandbox/restricted-local-sandbox.js
- E045 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-capability/dist/builtins/workspace-files/path-security.js
- E046 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-model/dist/providers/openai-compatible/response-handling.js
- E047 / original_verifier_code: C:\Project\nextagent-bench\datasets\c44fb04745607db4d1c0b07a945ec3fbdfaa2bd955ae172667aaa7edc95b4ae2\tasks\drone-planning-control\verifier\_oracle_sim.py
- E048 / original_verifier_code: C:\Project\nextagent-bench\datasets\c44fb04745607db4d1c0b07a945ec3fbdfaa2bd955ae172667aaa7edc95b4ae2\tasks\drone-planning-control\verifier\test_outputs.py
- E049 / workspace_artifact_inventory: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar
- E050 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/001.txt
- E051 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/002.txt
- E052 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/003.txt
- E053 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/004.txt
- E054 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/005.txt
- E055 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/006.txt
- E056 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/007.txt
- E057 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/008.txt
- E058 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/009.txt
- E059 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/010.txt
- E060 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/011.txt
- E061 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/012.txt
- E062 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/013.txt
- E063 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/014.txt
- E064 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/015.txt
- E065 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/016.txt
- E066 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/017.txt
- E067 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/018.txt
- E068 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/019.txt
- E069 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/020.txt
- E070 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/021.txt
- E071 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/022.txt
- E072 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/023.txt
- E073 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/024.txt
- E074 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/025.txt
- E075 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/026.txt
- E076 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/027.txt
- E077 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\drone-planning-control\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/commands/028.txt
