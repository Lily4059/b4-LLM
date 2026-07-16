# B4 个人部分仓库说明

本仓库是个人部分整理版，只保留 `PERSONAL_README_B4.md` 中 3.1 文件结构对应的核心内容，并额外保留展示所需的 `ai_web/` 与 `module_demos/` 两个前端演示文件夹。

## 重要说明

- `ai_web/` 和 `module_demos/` 的展示网页是基于整个 B1-B5 系统联动实现的。
- 当前仓库只上传个人部分与展示相关代码，不是完整团队仓库。
- 因此仓库中的 Web 页面、演示接口和部分脚本在脱离完整系统依赖时，可能无法直接跑通，这是预期现象。
- 本仓库的重点是展示 B4 模块实现、前端展示代码、配置样例与代表性输出产物。

## 上传范围

- B4 核心代码：`code/b4_local_agent_llm.py`
- B4 相关运行时：`code/b1_agent_runtime_1.py`
- 公共结构定义与 I/O 工具：`code/common/schemas.py`、`code/common/io_utils.py`、`code/common/path_utils.py`
- 模型配置：`configs/model.yaml`、`configs/model_new.yaml`
- B4 相关消息样例：`data/messages/`
- 展示前端：`ai_web/`、`module_demos/`
- 代表性输出：`outputs/B4_llm/`、`outputs/B4_compat/`、`outputs/B3/compare_tools_injection/`、`outputs/full_demo/`
- 个人说明文档：`PERSONAL_README_B4.md`
- 功能索引文档：`b4-feature-guide.html`

## 目录结构

```text
agent/
├── code/
│   ├── b4_local_agent_llm.py
│   ├── b1_agent_runtime_1.py
│   └── common/
│       ├── schemas.py
│       ├── io_utils.py
│       └── path_utils.py
├── configs/
│   ├── model.yaml
│   └── model_new.yaml
├── data/
│   └── messages/
├── outputs/
│   ├── B4_llm/
│   ├── B4_compat/
│   ├── B3/compare_tools_injection/
│   └── full_demo/
├── ai_web/
├── module_demos/
├── PERSONAL_README_B4.md
└── b4-feature-guide.html
```

## 运行提示

- 如果你只查看 B4 代码与前端展示实现，本仓库内容已经足够。
- 如果你要真正启动完整 Web 对话或完整 Agent 流程，需要补齐团队系统中的其它模块与依赖环境。
