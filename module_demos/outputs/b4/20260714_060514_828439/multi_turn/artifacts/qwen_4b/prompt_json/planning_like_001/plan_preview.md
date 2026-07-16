# Plan-and-Execute 计划预览

1. 搜索 docs 目录中与 tool calling 相关的文件 [completed]
   - summary: 搜索完成，找到3个与tool calling相关的文件：docs/tool_calling.md（得分16.904）、docs/search_skill_demo.md（得分7.151）、docs/agent_intro.txt（得分4.575）
2. 读取最相关的文件内容 [completed]
   - summary: 已读取3个文件内容，包含Tool Calling机制、搜索技能演示和Agent系统组成说明。
3. 总结关键结论 [completed]
   - summary: 关键结论：
     - 共同关注点：
       1. 工具调用是Agent系统的核心能力，由模型决策、工具层执行。
       2. 强调消息闭环：模型发出请求，工具返回结果（ToolMessage），模型据此更新状态。
       3. 工具需具备校验与执行能力，确保操作安全准确。
     - 关键差异点：
       - 职责侧重：tool_calling.md 聚焦模型决策机制；search_skill_demo.md 侧重搜索工具的具体编排与验证；agent_intro.txt 从系统架构角度定义工具在整体中的位置。
       - 应用场景：前者为通用原则，后者为具体技能演示，前者为全局视角。
     - 结论与建议：
       在构建Agent时，应明确模型负责‘何时调用’，工具层负责‘如何执行’，运行时负责‘消息流转’。设计工具编排时，需确保ToolMessage能完整返回执行结果，以支持后续决策。搜索等具体技能应作为可插拔工具，通过统一接口集成到Agent循环中。
