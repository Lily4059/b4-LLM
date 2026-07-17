# Plan-and-Execute 计划预览

1. 首先读取docs/agent_intro.txt文件 [completed]
   - summary: Agent 系统通常由模型、工具、记忆和执行循环组成。工具调用让模型能够读取本地文件、执行计算，并把结果用于后续回答。Memory 为 Agent 提供全局知识和历史对话上下文。
2. 然后读取docs/tool_calling.md文件 [completed]
   - summary: # Tool Calling
     模型负责决定是否调用工具，工具层负责校验和执行，运行时负责维护消息闭环。
3. 比较两个文档的关注点差异 [completed]
   - summary: agent_intro.txt关注点包括模型、工具、记忆和执行循环。tool_calling.md关注点包括模型决定是否调用工具、工具层校验和执行以及运行时维护消息闭环。
