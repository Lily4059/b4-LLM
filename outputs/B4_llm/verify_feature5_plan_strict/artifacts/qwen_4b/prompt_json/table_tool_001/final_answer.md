表格文件 tables/results.csv 包含 3 行数据和 3 列，列结构如下：

1. **task**：任务类型，包含三个任务：read_file、calculate、search
2. **score**：任务得分，数值范围 88-98，平均分为 92.67
3. **latency**：延迟时间（秒），数值范围 3.1-20.5，平均延迟为 12.93 秒

预览数据：
- read_file: score=92, latency=15.2s
- calculate: score=98, latency=3.1s
- search: score=88, latency=20.5s

统计特征：calculate 任务得分最高但延迟最低，search 任务得分最低且延迟最高。
