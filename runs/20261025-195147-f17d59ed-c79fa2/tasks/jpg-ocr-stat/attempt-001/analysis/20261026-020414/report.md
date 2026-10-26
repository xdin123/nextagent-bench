# 分析未完成，需要核验

Diagnostic request failed: HTTP_401

Evidence packet retained where available; no unsupported root cause asserted. Retry diagnostics without rerunning the task.

原始回复见本目录 model-response.json / format-repair-response.json；不可把格式未验证的内容当作已证实根因。

## 已保存证据

- E001 / observed_result: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\jpg-ocr-stat\attempt-001\result.json
- E002 / effective_task: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\jpg-ocr-stat\attempt-001\agent-facing\prompt.txt
- E003 / path_and_skill_plan: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\jpg-ocr-stat\attempt-001\agent-facing\adaptation.json
- E004 / effective_runtime_configuration: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\jpg-ocr-stat\attempt-001\bootstrap.json
- E005 / skill_discovery: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\jpg-ocr-stat\attempt-001\skill-discovery.json
- E006 / startup_evidence: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\jpg-ocr-stat\attempt-001\runtime\na-start.log
- E007 / provided_skill_document: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\jpg-ocr-stat\attempt-001\agent-facing\skills\image-ocr\SKILL.md
- E008 / provided_skill_document: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\jpg-ocr-stat\attempt-001\agent-facing\skills\openai-vision\SKILL.md
- E009 / provided_skill_document: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\jpg-ocr-stat\attempt-001\agent-facing\skills\pdf\SKILL.md
- E010 / frozen_configuration: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\config\default-system.yaml
- E011 / frozen_configuration: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\config\agent.yaml
- E012 / frozen_configuration: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\config\changes.json
- E013 / frozen_configuration: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\config\quota.json
- E014 / framework_model_and_tool_boundaries: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\jpg-ocr-stat\attempt-001\nextagent-home\logs
- E015 / actual_model_request: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/jpg-ocr-stat/attempt-1/42aa074a0e404d819140a0d4733f1f4f/request.json
- E016 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/jpg-ocr-stat/attempt-1/42aa074a0e404d819140a0d4733f1f4f/request.json
- E017 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/jpg-ocr-stat/attempt-1/42aa074a0e404d819140a0d4733f1f4f/
- E018 / frozen_harness_code: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\adapter-upgrades\4f5d50753f4f23abc988562533a0deb321ea508210f2a493c734457a39d64064\source\runtime\helper.mjs
- E019 / frozen_harness_code: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\adapter-upgrades\4f5d50753f4f23abc988562533a0deb321ea508210f2a493c734457a39d64064\source\runtime\start.mjs
- E020 / operator_concurrency_history: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\concurrency-history.jsonl
- E021 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-app/package.json
- E022 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-model/dist/providers/openai-compatible/response-handling.js
- E023 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-model/dist/invocation/failure-recovery.js
- E024 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-capability/dist/builtins/skill-tool.js
- E025 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-capability/dist/builtins/python/python-tool.js
- E026 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-capability/dist/builtins/bash/bash-tool.js
- E027 / original_verifier_code: C:\Project\nextagent-bench\datasets\c44fb04745607db4d1c0b07a945ec3fbdfaa2bd955ae172667aaa7edc95b4ae2\tasks\jpg-ocr-stat\verifier\test_outputs.py
- E028 / workspace_artifact_inventory: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\jpg-ocr-stat\attempt-001\nextagent-home.tar
