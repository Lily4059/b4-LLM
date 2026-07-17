tables/results.csv 包含3行数据、3列，列结构如下：

| 列名 | 类型 | 说明 |
|------|------|------|
| task | 字符串 | 任务类型（如 read_file, calculate, search） |
| score | 数值 | 任务得分（范围：88-98，平均约92.67） |
| latency | 数值 | 任务延迟（单位未说明，范围：3.1-20.5，平均约12.93） |

预览数据：
- read_file: score=92, latency=15.2
- calculate: score=98, latency=3.1
- search: score=88, latency=20.5
