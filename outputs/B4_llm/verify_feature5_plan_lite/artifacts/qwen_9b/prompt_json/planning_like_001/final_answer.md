根据对 docs 目录中 tool calling 相关文件的搜索与读取，关键结论如下：

1. **核心职责划分**：
   - **Tool Calling 模型**：负责决定是否调用工具。
   - **工具层**：负责校验和执行工具。
   - **运行时**：负责维护消息闭环。

2. **工具编排流程**：
   - 模型先决定调用哪个工具。
   - 运行时执行工具并把 ToolMessage 返回给模型。

3. **验证文件**：
   - `docs/tool_calling.md` 是核心文档，详细描述了 tool calling 的模型职责。
   - `docs/search_skill_demo.md` 用于验证 local_file_search 工具，并展示了工具编排的实际应用示例。

总结：tool calling 机制强调模型与工具层的职责分离，通过运行时维护消息闭环，确保工具调用流程的正确性和可追溯性。
