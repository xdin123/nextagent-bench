# 评测结果入口

- [原全量结果整理](runs/20261025-195147-f17d59ed-c79fa2/RESULTS-SUMMARY.md)：87 题，39 题有评分；人工停止，未取得完整总分。
- [原全量 Excel](runs/20261025-195147-f17d59ed-c79fa2/results.xlsx)。
- [两题 Hook 补测结果](runs/20261026-161356-f17d59ed-b0c82d/RERUN-SUMMARY.md)：已完成，两题均因重复输出检测终止，原分数保留。
- [已完成的临时文件清理清单](runs/20261025-195147-f17d59ed-c79fa2/cleanup-manifest.json)：约 898.2 MiB；任务结果和复现输入保留。

正式结果和补测结果保存在各自的 runs 子目录，代码和运行配置位于 nextagent_bench、scripts、profiles 和项目根脚本。artifacts/datasets 为复现输入，.secrets 为加密凭据，.venv 为执行依赖，不作为临时文件删除。

- [本次两题边界轨迹合并文件](runs/20261026-161356-f17d59ed-b0c82d/exports/20261026T085450121014Z/completed-framework-traces.ndjson)：393行，范围及缺失项见补测结果说明。
