根据对 docs 目录中 tool calling 相关文件的搜索与读取，关键结论如下：

1. **核心职责划分**：
   - **Tool Calling 模型**：负责决定是否调用工具。
   - **工具层**：负责校验和执行工具调用。
   - **运行时**：负责维护消息闭环。

2. **工具编排流程**：
   - 模型先决定调用哪个工具。
   - 运行时执行工具并把 ToolMessage 返回给模型。

3. **验证文件**：
   - `docs/tool_calling.md` 提供了 tool calling 的核心概念和职责划分。
   - `docs/search_skill_demo.md` 提供了工具编排的演示文档，用于验证 local_file_search 工具。

总结：tool calling 的核心在于模型决策、工具执行和运行时消息闭环的协同工作。
