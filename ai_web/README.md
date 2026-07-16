## Agent Studio Web

此目录提供一个纯 Python 的本地 Web UI，用于操作增强版 Agent Runtime、工具、记忆、模型配置、批量任务与执行追踪。

### 启动

在项目根目录下执行：

```powershell
python .\ai_web\server.py
```

浏览器打开：

```
http://127.0.0.1:8010/
```

### 说明

- `server.py` 默认加载增强版 `server_1.py`、`index_1.html` 与 `app_1.js`。
- 对话页支持多轮输入、多次工具循环、中断恢复、历史摘要压缩、System Prompt 切换/追加、工具结果缓存和模型 profile 选择。
- 批量任务页支持输入批量 JSON 文件路径或直接粘贴任务 JSON。
- Memory 页支持关键词/向量 Top-K 检索、指定文档更新与冲突策略、错误 Memory 影响分析。
- API 会把运行产物写入 `outputs/web_ui/`；可通过 `--host` 和 `--port` 修改监听地址。

### 性能说明

- Web 后台任务在服务器进程内执行，本地模型只加载一次，后续对话复用模型缓存。
- 服务启动后会在后台预热 `model.yaml` 的默认模型；首次加载仍取决于模型大小、磁盘和 GPU，后续请求会明显更快。
- 默认使用“普通对话模式（快速）”；复杂多步骤任务再选择 Plan 或智能执行。
- 发送给模型的原始聊天记录限制为最近 12 条，长期用户要求仍会从完整会话历史提取为 System 上下文。
- 如需关闭启动预热，可使用 `python .\ai_web\server.py --no-warmup`。
