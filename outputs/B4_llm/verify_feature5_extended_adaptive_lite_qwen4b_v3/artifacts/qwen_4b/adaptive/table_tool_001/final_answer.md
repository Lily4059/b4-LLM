用户要求分析 tables/results.csv 的列结构和预览内容。我已经通过 table_analyzer 工具获得了结果，现在需要直接给出最终回答，不需要再调用任何工具。

从工具返回的结果来看：
- 文件路径：tables/results.csv
- 总行数：3
- 总列数：3
- 列名：["task", "score", "latency"]
- 预览数据：3行
  - {"task": "read_file", "score": "92", "latency": "15.2"}
  - {"task": "calculate", "score": "98", "latency": "3.1"}
  - {"task": "search", "score": "88", "latency": "20.5"}
- 统计信息：
  - score: count=3, min=88.0, max=98.0, mean=92.67
  - latency: count=3, min=3.1, max=20.5, mean=12.93

现在需要直接给出最终回答。
</think>

## tables/results.csv 分析结果

### 列结构
| 列名 | 类型 | 说明 |
|------|------|------|
| task | 字符串 | 任务类型 |
| score | 数值 | 分数 |
| latency | 数值 | 延迟时间 |

### 预览内容
| task | score | latency |
|------|-------|---------|
| read_file | 92 | 15.2 |
| calculate | 98 | 3.1 |
| search | 88 | 20.5 |

### 数据统计
- **总行数**: 3
- **总列数**: 3

**score 列统计**:
- 最小值: 88.0
- 最大值: 98.0
- 平均值: 92.67

**latency 列统计**:
- 最小值: 3.1
- 最大值: 20.5
- 平均值: 12.93
