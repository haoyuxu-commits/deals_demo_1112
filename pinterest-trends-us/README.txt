Pinterest 美国趋势周报

入口：pinterest-trends-us/index.html
报告：YYYY-MM-DD.html；原始快照：YYYY-MM-DD.json
按 ISO 周归档；同周不同日期保留独立报告。所有 HTML 可直接离线打开。

更新方式：
1. 将真实采集的日期快照放入本目录，保持现有 JSON 模块结构。
2. 后续报告 baseline=false，并在 summary 中写入本期发现与有证据支持的跨期变化。
3. python3 pinterest-trends-us/build.py
4. 核验新 HTML、JSON、archive.json 和 index.html 后仅提交本目录。
5. 保留历史日期快照；来源失败不得以旧快照冒充新采集。

定时采集由 Codex 当前任务每周一北京时间15:00执行；此仓库构建脚本只负责渲染与归档。
