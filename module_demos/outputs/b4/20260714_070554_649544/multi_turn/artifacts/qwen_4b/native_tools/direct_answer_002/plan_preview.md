# Plan-and-Execute 计划预览

1. 请用三句话说明 ReAct 和 Plan-and-Execute 的区别。 [completed]
   - summary: ReAct 和 Plan-and-Execute 的区别如下：
     1. **执行方式不同**：ReAct 采用“思考-行动-观察”的循环模式，在每一步行动后都会根据观察结果动态调整后续计划；而 Plan-and-Execute 先制定完整计划再按顺序执行，中间不根据反馈调整。
     2. **灵活性差异**：ReAct 在遇到障碍时可以即时调整策略，适合处理不确定性和需要探索的任务；Plan-and-Execute 更适合目标明确、步骤固定的任务，执行效率更高。
     3. **适用场景不同**：ReAct 常用于需要多步推理和动态决策的复杂任务（如代码调试、科学探索）；Plan-and-Execute 更适合结构化任务（如数据清洗、文档处理）等确定性较高的场景。
