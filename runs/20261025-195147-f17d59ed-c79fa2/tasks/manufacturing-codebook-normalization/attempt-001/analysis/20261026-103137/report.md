# 分析未完成，需要核验

Diagnostic request failed: HTTP_502

Evidence packet retained where available; no unsupported root cause asserted. Retry diagnostics without rerunning the task.

原始回复见本目录 model-response.json / format-repair-response.json；不可把格式未验证的内容当作已证实根因。

## 已保存证据

- E001 / observed_result: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\manufacturing-codebook-normalization\attempt-001\result.json
- E002 / effective_task: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\manufacturing-codebook-normalization\attempt-001\agent-facing\prompt.txt
- E003 / path_and_skill_plan: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\manufacturing-codebook-normalization\attempt-001\agent-facing\adaptation.json
- E004 / physical_path_evidence: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\manufacturing-codebook-normalization\attempt-001\path-bridge.json
- E005 / effective_runtime_configuration: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\manufacturing-codebook-normalization\attempt-001\bootstrap.json
- E006 / skill_discovery: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\manufacturing-codebook-normalization\attempt-001\skill-discovery.json
- E007 / verifier_assertions: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\manufacturing-codebook-normalization\attempt-001\ctrf.json
- E008 / verifier_output: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\manufacturing-codebook-normalization\attempt-001\verifier-stdout.txt
- E009 / startup_evidence: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\manufacturing-codebook-normalization\attempt-001\runtime\na-start.log
- E010 / provided_skill_document: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\manufacturing-codebook-normalization\attempt-001\agent-facing\skills\manufacturing-failure-reason-codebook-normalization\SKILL.md
- E011 / frozen_configuration: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\config\default-system.yaml
- E012 / frozen_configuration: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\config\agent.yaml
- E013 / frozen_configuration: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\config\changes.json
- E014 / frozen_configuration: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\config\quota.json
- E015 / canonical_execution_timeline: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\manufacturing-codebook-normalization\attempt-001\trajectory.jsonl
- E016 / framework_model_and_tool_boundaries: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\manufacturing-codebook-normalization\attempt-001\nextagent-home\logs
- E017 / actual_model_request: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261026-092302-52f9f9\exchanges.tar!evidence/manufacturing-codebook-normalization/attempt-1/9f273d563c344eedaa964caae15e1c83/request.json
- E018 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261026-092302-52f9f9\exchanges.tar!evidence/manufacturing-codebook-normalization/attempt-1/9f273d563c344eedaa964caae15e1c83/request.json
- E019 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261026-092302-52f9f9\exchanges.tar!evidence/manufacturing-codebook-normalization/attempt-1/9f273d563c344eedaa964caae15e1c83/
- E020 / actual_model_request: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261026-092302-52f9f9\exchanges.tar!evidence/manufacturing-codebook-normalization/attempt-1/34cfb435ff1e453ca8bd4755e5f2e975/request.json
- E021 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261026-092302-52f9f9\exchanges.tar!evidence/manufacturing-codebook-normalization/attempt-1/34cfb435ff1e453ca8bd4755e5f2e975/request.json
- E022 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261026-092302-52f9f9\exchanges.tar!evidence/manufacturing-codebook-normalization/attempt-1/34cfb435ff1e453ca8bd4755e5f2e975/
- E023 / actual_model_request: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261026-092302-52f9f9\exchanges.tar!evidence/manufacturing-codebook-normalization/attempt-1/811b79befd4345e4a4972224448ca268/request.json
- E024 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261026-092302-52f9f9\exchanges.tar!evidence/manufacturing-codebook-normalization/attempt-1/811b79befd4345e4a4972224448ca268/request.json
- E025 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261026-092302-52f9f9\exchanges.tar!evidence/manufacturing-codebook-normalization/attempt-1/811b79befd4345e4a4972224448ca268/
- E026 / actual_model_request: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261026-092302-52f9f9\exchanges.tar!evidence/manufacturing-codebook-normalization/attempt-1/56236b9d726e44ae807a5f0f21dfa8b5/request.json
- E027 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261026-092302-52f9f9\exchanges.tar!evidence/manufacturing-codebook-normalization/attempt-1/56236b9d726e44ae807a5f0f21dfa8b5/request.json
- E028 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261026-092302-52f9f9\exchanges.tar!evidence/manufacturing-codebook-normalization/attempt-1/56236b9d726e44ae807a5f0f21dfa8b5/
- E029 / actual_model_request: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261026-092302-52f9f9\exchanges.tar!evidence/manufacturing-codebook-normalization/attempt-1/b3971ac313954412b7fe9c0211dee19c/request.json
- E030 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261026-092302-52f9f9\exchanges.tar!evidence/manufacturing-codebook-normalization/attempt-1/b3971ac313954412b7fe9c0211dee19c/request.json
- E031 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261026-092302-52f9f9\exchanges.tar!evidence/manufacturing-codebook-normalization/attempt-1/b3971ac313954412b7fe9c0211dee19c/
- E032 / actual_model_request: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261026-092302-52f9f9\exchanges.tar!evidence/manufacturing-codebook-normalization/attempt-1/a40bcdeb6cc14ab19d6b2c546e7cfbc9/request.json
- E033 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261026-092302-52f9f9\exchanges.tar!evidence/manufacturing-codebook-normalization/attempt-1/a40bcdeb6cc14ab19d6b2c546e7cfbc9/request.json
- E034 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261026-092302-52f9f9\exchanges.tar!evidence/manufacturing-codebook-normalization/attempt-1/a40bcdeb6cc14ab19d6b2c546e7cfbc9/
- E035 / joined_tool_boundaries: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\manufacturing-codebook-normalization\attempt-001\tool-boundary-checks.json
- E036 / frozen_harness_code: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\adapter-upgrades\4f5d50753f4f23abc988562533a0deb321ea508210f2a493c734457a39d64064\source\runtime\helper.mjs
- E037 / frozen_harness_code: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\adapter-upgrades\4f5d50753f4f23abc988562533a0deb321ea508210f2a493c734457a39d64064\source\runtime\start.mjs
- E038 / operator_concurrency_history: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\concurrency-history.jsonl
- E039 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-model/dist/providers/openai-compatible/response-handling.js
- E040 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-model/dist/invocation/failure-recovery.js
- E041 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-capability/dist/builtins/skill-tool.js
- E042 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-capability/dist/builtins/python/python-tool.js
- E043 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-capability/dist/builtins/bash/bash-tool.js
- E044 / original_verifier_code: C:\Project\nextagent-bench\datasets\c44fb04745607db4d1c0b07a945ec3fbdfaa2bd955ae172667aaa7edc95b4ae2\tasks\manufacturing-codebook-normalization\verifier\test_outputs.py
- E045 / workspace_artifact_inventory: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\manufacturing-codebook-normalization\attempt-001\nextagent-home.tar
- E046 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\manufacturing-codebook-normalization\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/data/codebook_P1_POWER.csv
- E047 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\manufacturing-codebook-normalization\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/data/codebook_P2_CTRL.csv
- E048 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\manufacturing-codebook-normalization\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/data/codebook_P3_RF.csv
