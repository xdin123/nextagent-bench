# 分析未完成，需要核验

Diagnostic request failed: ANALYSIS_TIMEOUT

Evidence packet retained where available; no unsupported root cause asserted. Retry diagnostics without rerunning the task.

原始回复见本目录 model-response.json / format-repair-response.json；不可把格式未验证的内容当作已证实根因。

## 已保存证据

- E001 / observed_result: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\azure-bgp-oscillation-route-leak\attempt-001\result.json
- E002 / effective_task: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\azure-bgp-oscillation-route-leak\attempt-001\agent-facing\prompt.txt
- E003 / path_and_skill_plan: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\azure-bgp-oscillation-route-leak\attempt-001\agent-facing\adaptation.json
- E004 / physical_path_evidence: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\azure-bgp-oscillation-route-leak\attempt-001\path-bridge.json
- E005 / effective_runtime_configuration: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\azure-bgp-oscillation-route-leak\attempt-001\bootstrap.json
- E006 / skill_discovery: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\azure-bgp-oscillation-route-leak\attempt-001\skill-discovery.json
- E007 / verifier_assertions: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\azure-bgp-oscillation-route-leak\attempt-001\ctrf.json
- E008 / verifier_output: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\azure-bgp-oscillation-route-leak\attempt-001\verifier-stdout.txt
- E009 / startup_evidence: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\azure-bgp-oscillation-route-leak\attempt-001\runtime\na-start.log
- E010 / provided_skill_document: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\azure-bgp-oscillation-route-leak\attempt-001\agent-facing\skills\azure-bgp\SKILL.md
- E011 / frozen_configuration: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\config\default-system.yaml
- E012 / frozen_configuration: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\config\agent.yaml
- E013 / frozen_configuration: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\config\changes.json
- E014 / frozen_configuration: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\config\quota.json
- E015 / canonical_execution_timeline: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\azure-bgp-oscillation-route-leak\attempt-001\trajectory.jsonl
- E016 / framework_model_and_tool_boundaries: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\azure-bgp-oscillation-route-leak\attempt-001\nextagent-home\logs
- E017 / actual_model_request: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/azure-bgp-oscillation-route-leak/attempt-1/ca1c7ba3a50844d898da8fc10e573bb7/request.json
- E018 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/azure-bgp-oscillation-route-leak/attempt-1/ca1c7ba3a50844d898da8fc10e573bb7/request.json
- E019 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/azure-bgp-oscillation-route-leak/attempt-1/ca1c7ba3a50844d898da8fc10e573bb7/
- E020 / actual_model_request: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/azure-bgp-oscillation-route-leak/attempt-1/557aa0a1d156446cb34c49984ce2e8b0/request.json
- E021 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/azure-bgp-oscillation-route-leak/attempt-1/557aa0a1d156446cb34c49984ce2e8b0/request.json
- E022 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/azure-bgp-oscillation-route-leak/attempt-1/557aa0a1d156446cb34c49984ce2e8b0/
- E023 / actual_model_request: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/azure-bgp-oscillation-route-leak/attempt-1/115b8db31e904e0889bc2158ab04e7b0/request.json
- E024 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/azure-bgp-oscillation-route-leak/attempt-1/115b8db31e904e0889bc2158ab04e7b0/request.json
- E025 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/azure-bgp-oscillation-route-leak/attempt-1/115b8db31e904e0889bc2158ab04e7b0/
- E026 / actual_model_request: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/azure-bgp-oscillation-route-leak/attempt-1/f6f0836f1dac4f5bb023d7fab916c671/request.json
- E027 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/azure-bgp-oscillation-route-leak/attempt-1/f6f0836f1dac4f5bb023d7fab916c671/request.json
- E028 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/azure-bgp-oscillation-route-leak/attempt-1/f6f0836f1dac4f5bb023d7fab916c671/
- E029 / actual_model_request: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/azure-bgp-oscillation-route-leak/attempt-1/93e8e6b5840c464ab074cbfc4b930232/request.json
- E030 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/azure-bgp-oscillation-route-leak/attempt-1/93e8e6b5840c464ab074cbfc4b930232/request.json
- E031 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/azure-bgp-oscillation-route-leak/attempt-1/93e8e6b5840c464ab074cbfc4b930232/
- E032 / joined_tool_boundaries: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\azure-bgp-oscillation-route-leak\attempt-001\tool-boundary-checks.json
- E033 / frozen_harness_code: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\adapter-source\runtime\helper.mjs
- E034 / frozen_harness_code: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\adapter-source\runtime\start.mjs
- E035 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-platform-gateway-local/dist/sandbox/restricted-local-sandbox.js
- E036 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-capability/dist/builtins/workspace-files/path-security.js
- E037 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-model/dist/duplication-detection/controller.js
- E038 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-model/dist/duplication-detection/detection.js
- E039 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-model/dist/providers/openai-compatible/response-handling.js
- E040 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-model/dist/invocation/failure-recovery.js
- E041 / original_verifier_code: C:\Project\nextagent-bench\datasets\c44fb04745607db4d1c0b07a945ec3fbdfaa2bd955ae172667aaa7edc95b4ae2\tasks\azure-bgp-oscillation-route-leak\verifier\test_outputs.py
- E042 / workspace_artifact_inventory: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\azure-bgp-oscillation-route-leak\attempt-001\nextagent-home.tar
- E043 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\azure-bgp-oscillation-route-leak\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/data/local_pref.json
- E044 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\azure-bgp-oscillation-route-leak\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/data/possible_solutions.json
- E045 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\azure-bgp-oscillation-route-leak\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/data/preferences.json
- E046 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\azure-bgp-oscillation-route-leak\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/data/relationships.json
- E047 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\azure-bgp-oscillation-route-leak\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/data/route.json
- E048 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\azure-bgp-oscillation-route-leak\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/data/route_events.json
- E049 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\azure-bgp-oscillation-route-leak\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/data/topology.json
- E050 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\azure-bgp-oscillation-route-leak\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/environment/data/azuredeploy.json
- E051 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\azure-bgp-oscillation-route-leak\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/environment/data/azuredeploy.parameters.json
- E052 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\azure-bgp-oscillation-route-leak\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/environment/data/metadata.json
