# 个人模块 README

> 说明：本模板适用于 B 方向 Agent 智能体实训。B4 模块负责本地 LLM 推理与工具决策，同时个人还负责整体前端实现（Agent Studio Web 与 Module Studio 模块演示系统）。

---

## 1. 模块概述

### 1.1 模块名称

`B4 Agent LLM 决策模块 + 整体前端实现`

### 1.2 模块说明

B4 是 Agent 系统中负责 LLM 推理与工具决策的核心模块。它不直接读文件、不直接执行工具，只做一件事：接收上下文，调用本地 LLM，输出"下一步该调用什么工具"的结构化指令。

```text
B4 围绕三个核心抽象构建：

1. messages — 完整的对话消息列表，包含 system（系统指令）、user（用户输入）、assistant（模型历史回复）、tool（工具执行结果）四种角色。messages 是 B4 推理的全部上下文基础。

2. tools_schema — 当前可用工具的 JSON Schema 定义列表。每个工具包含 name、description、parameters 的 JSON Schema。决定了 LLM 能选择哪些工具。

3. AIMessage — B4 的输出产物。标准格式包含 content（文本回答）和 tool_calls（工具调用请求数组）。格式完全兼容 LangChain 消息协议。

B4 在 B1-B5 协作链路中出现两次：第一次产出 tool_calls 交给 B3/B2 执行，第二次看到所有 ToolMessage 结果后产出最终回答。将 LLM 推理与工具执行解耦的设计，让 B4 可以独立测试——只要给它 messages 和 tools_schema 就能验证推理结果，不需要真正执行任何工具。

除 B4 模块本身外，本人还负责整体前端实现：
1. Agent Studio Web（ai_web/）— 面向用户的一体化 Web 交互界面，六页面对话系统，支持模型切换/执行方式/记忆策略；集成 UI 人性化展示（工具调用自然语言描述、协议消息过滤、相邻消息去重合并）、模型预热（异步加载 + 任务注册）、B4 评测数据目录映射；
2. B4 个人前端的适应性调整：在 Module Studio 中为 B4 模块定制演示页面，B4 模块支持 6 大演示模式：单轮 AI 消息生成与多工具调用、多轮推理策略展示、模型切换与路由、工具调用模式对比、批量评估、计划状态管理 / 执行引擎观测。
```

### 1.3 完成情况概览

| 类型 | 完成情况 |
|---|---|
| 基础要求 | 已完成 model.yaml 读取、本地模型加载 Qwen3.5-4B 、tools_schema 接收与绑定、messages 接收、模型原始输出解析为标准 AIMessage（含 content 或 tool_calls）、raw_model_output.json 与 ai_message.json 记录。支持 mock、prompt_json 两种基础模式。 |
| 进阶要求 | 已完成 5 项要求进阶功能（F1-F5）和 6 项扩展增强（E1-E6）。F1 多工具并行调用、F2 Plan-and-Execute 多步规划（四状态标记驱动）、F3 本地模型切换（多 profile + 缓存）、F4 双模式对比（prompt_json vs native_tools + fallback）、F5 批量评估框架（五维指标 + CSV/JSON 报告）。E1 工具结果压缩（按工具类型定制）、E2 证据充分性校验（防幻觉式跳步）、E3 Reflexion 重规划（结构化错误三元组 + 三步修复）、E4 Human-in-the-Loop（三种场景 A/B/C 选项）、E5 自适应路由（启发式 + LLM 双级分类）、E6 工具结果缓存（发出前去重 + 跨步骤缓存）。 |
| 可独立运行的演示 | `python b4_local_agent_llm.py --model_config ../configs/model.yaml --messages ../data/messages/messages_no_tool.json --tools_schema ../data/messages/tools_schema_basic.json --mode prompt_json --outdir ../outputs/B4_llm/no_tool_real`；Module Studio 前端演示（6 个 B4 模块）：`python module_demos/run_all_demo.py`，浏览器打开 http://127.0.0.1:8100/#b4；Agent Studio Web 演示：`python ai_web/server.py --host 127.0.0.1 --port 8010`，浏览器打开 http://127.0.0.1:8010/；B4 主要评测产物位于 `module_demos/outputs/b4/` |
| 与团队系统集成情况 | B1 在每轮 Agent Loop 中调用 `b4_local_agent_llm.generate_ai_message()`，传入 messages、tools_schema、model_config 和推理模式，接收标准 AIMessage。完整系统通过 `run_full_demo.py` 或 Agent Studio Web 调用。Plan-and-Execute 和自适应执行通过 `b1_agent_runtime_1` 模块委托调用。 |

---

## 2. 环境、模型与数据依赖

### 2.1 运行环境

| 项目 | 要求 |
|---|---|
| Python 版本 | Python 3.10 |
| 必要依赖 | PyTorch 2.7.1、Transformers 5.12.1、Accelerate、PyYAML、NumPy、SentencePiece、Safetensors |
| 是否需要模型 | 需要（prompt_json 和 native_tools 模式；mock 模式不需要） |
| 是否需要 GPU | prompt_json 和 native_tools 模式需要 NVIDIA GPU（推荐 CUDA 11.8）；mock 模式不需要 |
| 是否需要外部数据集 | 不需要训练数据集，使用预设 messages 和 tools_schema 样例 |

### 2.2 模型依赖

| 模型 | 来源 | 项目内相对路径 | 用途 |
|---|---|---|---|
| Qwen3.5-4B | [ModelScope](https://huggingface.co/Qwen/Qwen3.5-4B) | `configs/model.yaml` 中配置为 `/root/siton-tmp/assignment_B/Qwen3.5-4B` | 主模型，用于 prompt_json 和 native_tools 推理 |
| Qwen2.5-7B | [ModelScope](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct) | `configs/model.yaml` 的 `model_pool.qwen_7b` 中配置 | 对比模型，用于模型切换和批量评测 |

```bash
# 模型权重不提交到仓库
# 如模型不在默认服务器路径，需修改 configs/model.yaml 中所有 profile 的 model_name_or_path 和 tokenizer_name_or_path
```

### 2.3 数据集或样例数据依赖

| 数据或文件 | 来源 | 项目内相对路径 | 用途 |
|---|---|---|---|
| 文档样例目录 | 项目自带 | `data/docs/` | 提供文件检索、读取、总结任务使用的源文档 |
| 租房任务样例目录 | 自主编写 | `data/life_rent/` | 提供多文件对比、规划执行、约束分析等复杂任务数据 |
| 消息与评测样例目录 | 项目自带 | `data/messages/` | 提供 B4 独立运行、工具调用、多轮往返、注入方式对比和批量评测所需的消息样例与工具 Schema |

`data/docs/` 目录中的具体内容：

| 文件 | 用途 |
|---|---|
| `agent_intro.txt` | Agent 系统简介文档，适合验证基础文件读取与总结 |
| `search_skill_demo.md` | 搜索技能演示文档，适合验证“先搜索再读取”的任务 |
| `tool_calling.md` | 工具调用机制说明文档，适合验证与 tool calling 相关的搜索、读取和总结 |

`data/life_rent/` 目录中的具体内容：

| 文件 | 用途 |
|---|---|
| `listing_a.md` | 租房候选房源 A，用于多文件对比 |
| `listing_b.md` | 租房候选房源 B，用于多文件对比 |
| `listing_c.md` | 租房候选房源 C，用于多文件对比 |
| `requirements.md` | 用户租房约束与需求说明，用于规划和决策 |
| `chat_log_noise.txt` | 干扰信息样例，用于测试噪声数据下的筛选能力 |
| `model_performance_batch.json` | 模型表现批量测试数据 |
| `MODEL_PERFORMANCE_TEST.md` | 模型表现测试说明文档 |

`data/messages/` 目录中的具体内容：

| 文件 | 用途 |
|---|---|
| `messages_no_tool.json` | 基础生成：让模型先生成工具调用 |
| `messages_with_tool.json` | 工具结果回传后生成最终回答 |
| `messages_with_error_tool.json` | 工具失败后的模型回答 |
| `messages_no_tool_multi_call_test.json` | 多工具请求样例 |
| `messages_with_multi_tool_batch_test.json` | 多 ToolMessage 回传样例 |
| `messages_life_rent_multi_read.json` | 基于租房数据的多文件读取样例 |
| `messages_life_rent_plan_execute.json` | 基于租房数据的 Plan-and-Execute 样例 |
| `messages_tools_compare.json` | 注入方式对比样例 |
| `messages_no_tool_new.json` | 额外的基础生成消息样例 |
| `messages_with_tool_new.json` | 额外的工具结果回传消息样例 |
| `tools_schema_basic.json` | 预置工具说明 |
| `ai_message_with_tool_calls.json` | 标准 AIMessage 中包含 tool_calls 的示例 |
| `eval_cases_feature5.json` | 6 条批量评测样例 |
| `eval_cases_feature5_extended.json` | 22 条扩展评测样例 |
| `eval_cases_life_rent.json` | 租房任务评测样例 |
| `b3_schema_description_eval_cases.json` | B3 Schema 描述评测用例 |
| `b3_tool_call_code_executor_valid.json` | B3 代码执行器有效调用样例 |
| `b3_tool_call_format_converter_valid.json` | B3 格式转换工具有效调用样例 |
| `b3_tool_call_missing_required.json` | B3 缺少必填参数的异常样例 |
| `b3_tool_call_read_convert_file_valid.json` | B3 读取并转换文件的有效调用样例 |
| `b3_tool_call_unknown_tool.json` | B3 未知工具调用异常样例 |
| `b3_tool_calls_batch_stats.json` | B3 工具调用批量统计样例 |

```bash
# B4 依赖的数据主要来自 data/docs、data/life_rent、data/messages 三类目录
# 所有样例文件均已在仓库中提供，无需额外下载
```

### 2.4 安装步骤

```bash
conda create -n agent_zhang python=3.10 -y
conda activate agent_zhang
cd agent
pip install -r requirements.txt
```

个人模块最小依赖上，`mock` 模式可以不加载真实模型；`prompt_json` 和 `native_tools` 模式需要完整的本地模型推理依赖（PyTorch + Transformers 依赖和 NVIDIA GPU等）。

---

## 3. 文件结构与接口边界

### 3.1 文件结构

```text
agent/
├── code/
│   ├── b4_local_agent_llm.py          # B4 核心模块：模型加载、推理、双模式工具调用、Plan-and-Execute、自适应路由、扩展增强（约 2800 行）
│   ├── b1_agent_runtime_1.py           # B1 Agent 运行时（B4 的 Plan-and-Execute 委托调用此模块）
│   └── common/
│       ├── schemas.py                 # AIMessage 标准数据结构与校验
│       ├── io_utils.py                 # JSON/YAML 读写工具
│       └── path_utils.py               # 路径解析工具
├── configs/
│   ├── model.yaml                     # 模型配置：后端、路径、模型池（default/planner/qwen_4b/qwen_7b）、路由策略、生成参数
│   └── model_new.yaml                 # 模块演示用模型配置
├── data/
│   └── messages/
│       ├── messages_no_tool.json      # 演示1输入：生成 tool_call
│       ├── messages_with_tool.json    # 演示2输入：生成最终回答
│       ├── messages_with_error_tool.json  # 演示3输入：工具失败后回答
│       ├── messages_with_multi_tool_batch_test.json  # 多工具往返输入
│       ├── messages_life_rent_plan_execute.json  # Plan-and-Execute 输入
│       ├── tools_schema_basic.json    # 预设工具说明
│       ├── eval_cases_feature5.json   # 6条评测用例
│       └── eval_cases_feature5_extended.json  # 22条扩展评测用例
├── outputs/
│   ├── B4_llm/                        # B4 命令行运行产物目录
│   ├── B4_compat/                     # 批量对比评测结果
│   ├── B3/compare_tools_injection/    # 注入方式对比结果
│   └── full_demo/                     # 完整系统演示产物
│       ├── demo_report.md
│       └── llm_calls/                 # 每次 LLM 调用的 raw_model_output + ai_message
├── ai_web/                            # Agent Studio Web 前端（本人负责）
│   ├── server.py                      # 统一 Web 服务端（ThreadingHTTPServer，六页面 API；UI 人性化展示：工具调用自然语言描述、协议消息过滤、相邻消息去重合并；模型预热：异步加载 + JOB_REGISTRY 任务注册；B4 评测目录映射：B4_FIXED_EVAL_DIRS）
│   ├── static/
│   │   ├── index.html                 # 前端页面（侧边栏导航 + 六页面切换 + 实时进度轮询）
│   │   ├── app.js                     # 前端交互逻辑（状态管理、API 调用、消息渲染、执行步骤展示）
│   │   └── app_1.js                   # 增强版前端（集成 B1+B4 的完整 Agent 对话）
│   └── README.md
├── module_demos/                      # Module Studio 模块演示系统（本人负责）
│   ├── demo_server.py                # 演示服务端（B1-B5 统一路由；B4 支持 6 大模式）
│   ├── run_all_demo.py                # 统一启动入口
│   ├── outputs/
│   │   └── b4/                        # B4 模块演示与评测产物（演示输出 + 批量评测结果 + 注入对比结果 + 模型路由可视化）
│   ├── static/
│   │   ├── index.html                 # 模块演示页面（左侧模块导航 + 右侧输入输出面板）
│   │   ├── app.js                     # 演示交互逻辑（6 大 B4 模式切换 + 参数输入 + 结果展示 + 在线人数感知）
│   │   ├── style.css                  # 演示页面样式
│   │   └── metrics.css                # 评测指标展示样式
│   └── README.md
├── run_full_demo.py                   # 完整系统一键演示入口
├── PERSONAL_README_B4.md              # 个人模块说明文档
└── b4-feature-guide.html              # B4 功能详解文档（含全部函数索引和行号）
```

### 3.2 接口边界

| 类型 | 来源 / 去向 | 数据格式 | 说明 |
|---|---|---|---|
| 输入 | B1 Agent Runtime 传入 messages | JSON 数组 | 包含 system、user、assistant、tool 角色的完整消息序列 |
| 输入 | B3 Tool Layer（经 B1 转发）传入 tools_schema | JSON 数组 | OpenAI 风格的工具说明，包含工具名称、描述和参数 Schema |
| 输入 | B1 传入 model_config | YAML 文件路径 | 模型路径、后端、生成参数、模型池和路由配置 |
| 输入 | B1 传入 mode | 字符串 | `mock`、`prompt_json` 或 `native_tools` |
| 输入 | B1 传入 forced_profile | 字符串或 None | 可选，强制指定模型 profile，覆盖路由策略 |
| 输出 | 返回给 B1 | JSON（B4Result） | 标准 AIMessage（含 content 或 tool_calls）、status、raw_record、trace、final_answer、profile_used |
| 输出 | 保存到 artifact_dir | JSON / JSONL / Markdown | raw_model_output.json、ai_message.json、llm_run_log.jsonl；Plan 模式额外输出 plan_preview.md、progress.md、trace.json |
| 前端 API | 浏览器 → Agent Studio Web | HTTP GET/POST | `/api/chat`（对话）、`/api/tools`（工具）、`/api/memory/index`（记忆）、`/api/config/model`（配置）、`/api/trace/latest`（追踪）、`/api/jobs`（任务状态）、`/api/presence`（在线状态） |
| 前端 API | 浏览器 → Module Studio | HTTP GET/POST | `/api/modules`（模块列表）、`/api/modules/b4/run`（B4 演示执行，支持 8 种 action）、`/api/modules/b4/eval_summary`（B4 评测汇总）、`/api/modules/b4/comparison`（B4 注入对比）、`/api/presence`（在线状态） |

---

## 4. 基础要求实现与演示

### 4.1 基础功能说明

```text
基础版本实现了以下功能：
1. 读取 model.yaml，加载本地 Qwen3.5-4B 模型配置（模型路径、tokenizer、dtype、device_map）；
2. 在一次任务开始时接收 tools_schema，完成工具绑定（注入 prompt 或传给模型原生接口）；
3. 接收 messages，调用本地 LLM 生成原始输出，并解析为包含 content 或 tool_calls 的标准 AIMessage；
4. 以 JSON 格式记录模型的原始输出（raw_model_output.json）与解析后的 AIMessage（ai_message.json）；
5. 支持 mock 模式（不加载真实模型，用固定逻辑模拟输出）和 prompt_json 模式（真实调用模型并将工具说明写入 prompt）。
```

### 4.2 基础功能实现路径

| 文件 / 函数 / 脚本 | 作用 |
|---|---|
| `b4_local_agent_llm.py::generate_ai_message` | B4 核心入口函数，统一管理模式路由、模型加载、推理生成和输出保存 |
| `b4_local_agent_llm.py::_load_model_config` | 读取 model.yaml 配置文件 |
| `b4_local_agent_llm.py::_resolve_runtime_mode` | 解析运行模式（mock / prompt_json / native_tools） |
| `b4_local_agent_llm.py::_prompt_json_generate` | prompt_json 模式生成：将 tools_schema 和格式约束注入 prompt，调用模型 generate |
| `b4_local_agent_llm.py::_mock_generate` | mock 模式生成：根据 messages 中是否已有 ToolMessage 返回固定 tool_call 或最终回答 |
| `b4_local_agent_llm.py::_parse_model_output` | 将模型原始文本输出解析为标准 AIMessage（content + tool_calls） |
| `b4_local_agent_llm.py::_parse_output_by_mode` | 按模式选择解析策略（prompt_json 解析 JSON / native_tools 解析 XML 块） |
| `common/schemas.py::make_ai_message` | 构造标准 AIMessage 并校验字段 |
| `common/schemas.py::validate_ai_message` | 校验 AIMessage 结构合法性 |
| `common/schemas.py::validate_messages` | 校验输入 messages 格式 |

基础流程：

```text
[model.yaml + messages + tools_schema] -> [模式路由] -> [模型加载/缓存] -> [prompt 构造与注入] -> [model.generate] -> [原始输出解析] -> [标准 AIMessage] -> [保存 JSON 产物]
```

关键代码片段（prompt 注入与输出解析）：

```python
# prompt_json 模式：将 tools_schema 注入 system prompt 并约束输出格式
def _prompt_json_generate(config_path, config, messages, tools_schema, selected_profile):
    merged_config = _merged_model_settings(config, selected_profile)
    model, tokenizer = _get_or_load_model(config_path, merged_config)
    prompt_messages = _prepare_chat_messages(messages)
    _normalize_assistant_tool_calls_for_chat_template(prompt_messages)
    # 将 tools_schema 格式化为 JSON 文本并追加到 system prompt
    tool_block = _format_tools_as_json_block(tools_schema)
    system_content = _append_text_block(
        prompt_messages[0].get("content", ""),
        tool_block + "\n" + _OUTPUT_FORMAT_INSTRUCTION
    )
    prompt_messages[0]["content"] = system_content
    # 调用模型生成
    input_ids = tokenizer.apply_chat_template(prompt_messages, add_generation_prompt=True, return_tensors="pt")
    output_ids = model.generate(input_ids, **generation_kwargs)
    raw_text = tokenizer.decode(output_ids[0][input_ids.shape[1]:], skip_special_tokens=True)
    return {"raw_text": raw_text, ...}

# 解析原始输出为标准 AIMessage
def _parse_model_output(raw_text):
    parsed = _extract_json_payload(raw_text)  # 从文本中提取 JSON
    content = str(parsed.get("content") or "")
    tool_calls = _normalize_tool_calls(parsed.get("tool_calls"))
    ai_message = make_ai_message(content, tool_calls)
    return parsed, validate_ai_message(ai_message)
```

### 4.3 基础功能输入格式与样例

| 字段 / 输入文件 | 类型 / 格式 | 是否必需 | 说明 |
|---|---|---|---|
| model_config | YAML 文件路径 | 是 | 模型路径、后端、生成参数 |
| messages | JSON 数组 | 是 | 完整消息序列 |
| tools_schema | JSON 数组 | 是 | 工具说明，格式同 OpenAI function calling |
| mode | 字符串 | 否 | 默认从 model.yaml 的 runtime.default_mode 读取 |

样例输入：

| 样例文件 | 用途 |
|---|---|
| `data/messages/messages_no_tool.json` | 验证模型生成 tool_call：messages 中只有 system 和 user，模型需要决定调用 file_reader |
| `data/messages/messages_with_tool.json` | 验证模型基于 ToolMessage 生成最终回答：messages 已包含 tool 角色消息 |
| `data/messages/messages_with_error_tool.json` | 验证工具调用失败后模型的回答能力 |

### 4.4 基础功能演示命令

```bash
cd agent/code

# 演示1：接收初始 messages，生成包含 tool_calls 的 AIMessage
python b4_local_agent_llm.py --model_config ../configs/model.yaml \
  --messages ../data/messages/messages_no_tool.json \
  --tools_schema ../data/messages/tools_schema_basic.json \
  --mode prompt_json --outdir ../outputs/B4_llm/no_tool_real

# 演示2：接收已包含 ToolMessage 的 messages，生成最终回答
python b4_local_agent_llm.py --model_config ../configs/model.yaml \
  --messages ../data/messages/messages_with_tool.json \
  --tools_schema ../data/messages/tools_schema_basic.json \
  --mode prompt_json --outdir ../outputs/B4_llm/with_tool_real

# 演示3：工具调用失败后的模型回答
python b4_local_agent_llm.py --model_config ../configs/model.yaml \
  --messages ../data/messages/messages_with_error_tool.json \
  --tools_schema ../data/messages/tools_schema_basic.json \
  --mode prompt_json --outdir ../outputs/B4_llm/error_tool_real

# 演示4：mock 模式（无 GPU 环境）
python b4_local_agent_llm.py --model_config ../configs/model.yaml \
  --messages ../data/messages/messages_no_tool.json \
  --tools_schema ../data/messages/tools_schema_basic.json \
  --mode mock --outdir ../outputs/B4_llm/no_tool_mock
```

运行后应观察以下现象：

- 终端打印输出目录路径，退出码为 0
- `outputs/B4_llm/<case>/raw_model_output.json` 中 `status` 为 `success`，`raw_text` 为模型原始输出
- `outputs/B4_llm/<case>/ai_message.json` 包含合法 AIMessage（content 非空或 tool_calls 非空）
- 演示1 的 ai_message 中 `content` 为空、`tool_calls` 包含 file_reader 调用
- 演示2 的 ai_message 中 `tool_calls` 为空、`content` 为基于工具结果的中文总结

### 4.5 基础功能输出格式

| 输出文件 / 返回字段 | 格式 | 说明 |
|---|---|---|
| `raw_model_output.json` | JSON | 模式、后端、原始文本、解析候选、状态、错误、尝试记录、Token 用量和时间戳 |
| `ai_message.json` | JSON | 标准 AIMessage：`role`、`content`、`tool_calls`（含 id、name、args） |
| `llm_run_log.jsonl` | JSONL | 每次调用的时间戳、模式、状态、输出路径和错误信息 |
| `generate_ai_message` 返回值 | JSON | `ai_message`、`status`、`error`、`raw_record`（含完整原始记录） |

### 4.6 基础功能结果截图

```text
[在此处插入基础功能运行截图]
[在此处插入关键输出文件截图]
```

示例占位：

![基础功能演示占位](docs/images/basic_feature_placeholder.png)

---

## 5. 进阶要求实现与演示

### 5.1 选择的进阶要求

| 进阶要求 | 是否完成 | 对应文件 / 函数 | 简要说明 |
|---|---|---|---|
| F1 多工具并行调用 | 是 | `_normalize_tool_calls`(L886)、`_dedupe_identical_resource_tool_calls`(L2066)、`merge_tool_messages`(L518) | 单轮发出多个 tool_calls，B3 并行执行后 B4 统一消费结果；发出前去重 + 接收后合并 |
| F2 Plan-and-Execute 多步规划 | 是 | `_run_plan_execute_impl`(L4043)、`normalize_plan_steps`(L1221)、`apply_step_marker`(L1609) | 三阶段流程（规划→执行→状态管理），四状态标记驱动步骤流转，步骤与工具调用自动匹配 |
| F3 本地模型切换 | 是 | `_resolve_model_profile`(L76)、`_MODEL_CACHE`(L22)、`_load_model_bundle`(L2329) | model_pool 支持 default/planner/qwen_4b/qwen_7b 动态切换，带线程安全缓存 |
| F4 双模式对比 | 是 | `_prompt_json_generate`(L2577)、`_native_tools_generate`(L2623)、`compare_tools_injection_modes`(L3236) | prompt_json 与 native_tools 两种工具注入方式，含 fallback 机制和自动对比评测 |
| F5 批量评估框架 | 是 | `run_batch_evaluation`(L3474)、`_evaluate_tool_mode_result`(L2877)、`_summarize_eval_rows`(L3446) | 遍历 profile×mode×case 笛卡尔积，五维指标，输出 CSV+JSON 报告 |

| 扩展功能 | 是否完成 | 对应文件 / 函数 | 简要说明 |
|---|---|---|---|
| E1 工具结果压缩 | 是 | `compress_tool_messages`(L686)、`_compress_file_reader_output`(L600)、`_compress_local_file_search_output`(L627)、`_compress_table_analyzer_output`(L654) | 按工具类型定制压缩策略，防上下文溢出 |
| E2 证据充分性校验 | 是 | `_has_sufficient_evidence`(L1872)、`_step_has_sufficient_evidence`(L1880)、`_required_distinct_file_count`(L1787)、`_distinct_successful_file_sources`(L1800) | 防幻觉式跳步，确认工具证据满足才允许 STEP_DONE；支持中文数字解析 |
| E3 Reflexion 重规划 | 是 | `_replan_hint_from_tool_failures`(L1508)、`_generate_with_retry`(L403) | 失败后生成结构化错误三元组，引导模型"诊断→候选→选择"三步修复 |
| E4 Human-in-the-Loop | 是 | `_build_budget_exhausted_ask_user`(L1949)、`_duplicate_resource_confirmation_text`(L2031) | 预算耗尽/重复资源/文件数不足三种场景下 A/B/C 选项暂停等待用户决策 |
| E5 自适应路由 | 是 | `classify_task_complexity`(L3596)、`_heuristic_task_complexity`(L3072)、`_run_adaptive_execute_impl`(L3977) | 简单任务直接回答（react_one_round），复杂任务自动走 Plan-and-Execute |
| E6 工具结果缓存 | 是 | `_dedupe_identical_resource_tool_calls`(L2066) + `tool_result_cache`(L4251) | 发出前去重（按签名）+ 跨步骤缓存（按 name+args_json），避免重复读取 |
| 前端 Module Studio | 是 | `module_demos/demo_server.py`、`module_demos/static/` | B1-B5 模块演示系统；B4 预置 8 种演示模式 + mock fixtures 回放 + 真实模型实时执行；在线人数感知；评测产物加载（eval_summary/comparison） |
| 前端 Agent Studio | 是 | `ai_web/server.py`、`ai_web/static/` | 六页面对话系统，支持模型切换/执行方式/记忆策略；UI 人性化展示（工具调用自然语言描述、协议消息过滤、消息去重合并）；模型异步预热 + 任务注册；B4 评测目录映射；实时进度轮询 |

### 5.2 进阶功能 1：F1 多工具并行调用

#### 功能说明

```text
F1 多工具并行调用：基础版本只支持单轮一个工具调用。进阶版本允许模型在一次 AIMessage 中生成多个 tool_calls（如同时读取两个文件），B3 可并行执行并返回多个 ToolMessage，B4 在下一轮基于全部工具结果生成最终回答。

完整消息闭环：system → user → assistant(tool_calls×N) → tool(结果1)+tool(结果2) → assistant(最终回答)。

发出前处理：_normalize_tool_calls 将模型各种输出格式（单个 dict 或 list）统一为 {id, name, args} 标准结构。_normalize_tool_call 从 name/args/arguments/parameters/input/function 多种字段名兼容提取，特殊处理 table_analyzer/file_reader 的 path 别名。_dedupe_identical_resource_tool_calls 基于 (name, resource_path, args_json) 签名去重，避免 B3 重复执行同一文件。

接收后处理：_latest_tool_message_batch 从消息列表尾部提取最近一批 tool 角色消息。merge_tool_messages 按 tool_call_id 去重合并，标记每个调用的成功/失败状态。_latest_tool_batch_guidance 基于最新一批工具结果生成指导文本（成功的不重复、失败的列出原因和重试建议）。
```

#### 实现路径

| 文件 / 函数 / 脚本 | 作用 |
|---|---|
| `b4_local_agent_llm.py::_normalize_tool_calls` (L886) | 将单个 dict 或 list 统一标准化为 list[dict] |
| `b4_local_agent_llm.py::_normalize_tool_call` (L828) | 标准化单个工具调用：从多种字段名提取并统一为 {id, name, args} |
| `b4_local_agent_llm.py::_dedupe_identical_resource_tool_calls` (L2066) | 基于 (name, resource_path, args_json) 签名去重 |
| `b4_local_agent_llm.py::merge_tool_messages` (L518) | 将连续 tool 消息按 tool_call_id 去重合并，标记成功/失败状态 |
| `b4_local_agent_llm.py::_latest_tool_message_batch` (L504) | 从消息列表尾部提取最近一批 tool 角色消息 |
| `b4_local_agent_llm.py::_latest_tool_batch_guidance` (L257) | 基于工具结果生成指导文本（成功的不重复、失败的列原因） |
| `b4_local_agent_llm.py::_normalize_assistant_tool_calls_for_chat_template` (L163) | 将 assistant 消息中的 tool_calls 标准化为 chat_template 兼容格式 |

#### 演示命令

```bash
cd agent/code

# 多工具往返演示（mock 模式，无需 GPU）
python b4_local_agent_llm.py --model_config ../configs/model_new.yaml \
  --messages ../data/messages/messages_no_tool_multi_call_test.json \
  --tools_schema ../data/messages/tools_schema_basic.json \
  --mode mock --outdir ../outputs/B4_llm/multi_tool_mock
```

#### 输出格式

| 输出文件 / 返回字段 | 格式 | 说明 |
|---|---|---|
| `ai_message.json` | JSON | 标准 AIMessage，tool_calls 可包含多个并行调用 |
| `raw_model_output.json` | JSON | 模型原始输出，记录每次调用的解析状态 |
| `messages.json` | JSON 数组 | 完整消息序列，含多 tool_calls 和多 ToolMessage 往返 |

#### 示例图片

```text
[在此处插入多工具并行调用运行截图]
```

示例占位：

![F1多工具并行调用占位](docs/images/f1_placeholder.png)

### 5.3 进阶功能 2：F2 Plan-and-Execute 多步规划

#### 功能说明

```text
F2 Plan-and-Execute：参考 HuggingGPT 论文，采用"先想后做"策略，将复杂任务拆解为步骤计划再逐步执行。三阶段流程：

阶段一——规划：LLM 不调用任何工具，只输出 JSON 格式计划。normalize_plan_steps 解析并编号，去重标题、标记 low_value。JSON 解析失败时 fallback_plan_steps 从用户文本按编号/分号/中文标点拆分提取步骤。

阶段二——执行：对每个 pending 步骤，_run_plan_execute_impl 将 plan_state 注入 messages 作为上下文（含当前步骤编号、已完成步骤 summary、工具调用记录），LLM 根据上下文决定调用哪个工具。步骤与工具调用的自动匹配通过 _match_plan_step_for_tool_calls 基于步骤标题关键词（如"搜索"→local_file_search、"读取"→file_reader）和文件路径关联实现。对搜索类步骤，_deterministic_plan_tool_calls 可直接生成确定性调用而不经 LLM。

阶段三——状态管理：LLM 通过四种文本标记驱动步骤流转，由 apply_step_marker 解析：
- STEP_DONE:N:summary → 标记步骤 completed，推进到下一个 pending 步骤
- STEP_FAIL:N:reason → 触发 Reflexion 修复提示
- PLAN_UPDATE:<json> → 保留已完成步骤，用新 JSON 替换后续计划
- ASK_USER:question → 暂停执行循环，等待用户输入

关键辅助：_propagate_step_evidence 实现跨步骤证据传播，当前步骤的工具结果可满足其他 pending 步骤时自动注入，避免重复读取。summarize_tool_round_for_step 汇总某步骤本轮工具结果，多文件时提示"直接输出对比结论"。
```

#### 实现路径

| 文件 / 函数 / 脚本 | 作用 |
|---|---|
| `b4_local_agent_llm.py::_run_plan_execute_impl` (L4043) | Plan-and-Execute 核心实现：计划生成 → 步骤循环（工具调用/证据校验/标记处理/预算/缓存/跨步传播） |
| `b4_local_agent_llm.py::normalize_plan_steps` (L1221) | 将计划 payload 标准化为 [{step, title, status, summary, error}] |
| `b4_local_agent_llm.py::build_plan_execute_instruction` (L1341) | 构建 Plan-and-Execute 系统指令，包含四种状态标记规则 |
| `b4_local_agent_llm.py::fallback_plan_steps` (L1302) | JSON 解析失败时从用户文本拆分提取步骤 |
| `b4_local_agent_llm.py::apply_step_marker` (L1609) | 解析 STEP_DONE/STEP_FAIL/PLAN_UPDATE 标记并更新 plan_state |
| `b4_local_agent_llm.py::_match_plan_step_for_tool_calls` (L1582) | 根据工具名+路径与步骤标题匹配分数，推断工具属于哪一步 |
| `b4_local_agent_llm.py::_expected_tools_for_step` (L1700) | 根据步骤标题推断所需工具集 |
| `b4_local_agent_llm.py::_deterministic_plan_tool_calls` (L1726) | 对搜索类步骤直接生成确定性 local_file_search 调用 |
| `b4_local_agent_llm.py::summarize_tool_round_for_step` (L2190) | 汇总某步骤本轮工具结果 |
| `b4_local_agent_llm.py::_write_plan_and_progress` (L1364) | 写出 plan_preview.md 和 progress.md，供前端轮询 |
| `b4_local_agent_llm.py::_propagate_step_evidence` (L2259) | 跨步骤证据传播 |

流程：

```text
[messages + tools_schema] -> [normalize_plan_steps 生成计划] -> [逐步：注入 plan_state] -> [模型生成 tool_calls] -> [_dedupe_identical_resource_tool_calls 去重] -> [B3 执行工具] -> [merge_tool_messages 合并结果] -> [apply_step_marker 更新步骤状态] -> [全部完成 → 生成最终回答]
```

#### 演示命令

```bash
cd agent/code

# Plan-and-Execute 真实模型演示
python b4_local_agent_llm.py --model_config ../configs/model.yaml \
  --messages ../data/messages/messages_life_rent_plan_execute.json \
  --tools_schema ../data/messages/tools_schema_basic.json \
  --tools_config ../configs/tools.yaml --toolset basic_tools \
  --plan_execute --max_turns 3 --max_plan_steps 4 \
  --evidence_policy lite --outdir ../outputs/B4_llm/plan_execute_real
```

#### 输出格式

| 输出文件 / 返回字段 | 格式 | 说明 |
|---|---|---|
| `plan_preview.md` | Markdown | 模型生成的执行计划预览（表格形式，含步骤编号/标题/状态） |
| `progress.md` | Markdown | 计划执行进度（已完成步骤/待执行步骤/失败步骤/状态汇总） |
| `trace.json` | JSON | 运行轨迹（turns 列表，每轮含 tool_calls、tool_results、step_number、marker） |
| `ai_message.json` | JSON | 最终生成的 AIMessage |

#### 示例图片

```text
[在此处插入 Plan-and-Execute 计划预览截图]
[在此处插入 progress.md 进度截图]
```

示例占位：

![F2 Plan-and-Execute占位](docs/images/f2_placeholder.png)

### 5.4 进阶功能 3：F3 本地模型切换

#### 功能说明

```text
F3 本地模型切换：通过 model_pool 机制支持多个模型 profile 的动态切换，不同阶段（规划/执行）或不同任务可用不同模型。

模型池配置：model.yaml 中定义四个 profile——default（qwen_4b，主推理）、planner（qwen_7b，增强规划推理）、qwen_4b（Qwen3.5-4B）、qwen_7b（Qwen2.5-7B）。每个 profile 包含独立的 model_name_or_path、tokenizer_name_or_path、dtype、device_map 和生成参数。

路由策略：_resolve_model_profile 的优先级链为 forced_profile（外部强制指定）→ routing 配置（model.yaml 中按阶段指定的 plan_profile/execute_profile）→ 消息特征判断（_classify_task_profile 启发式分类）。支持通过 generate_ai_message 的 forced_profile 参数从外部覆盖路由决策。

模型缓存机制：_MODEL_CACHE 字典加线程锁，key 为 (model_path, tokenizer_path, ...) 元组，value 为 (tokenizer, model) 元组。切换 profile 时如果配置相同则复用已加载实例，避免 7B 模型重复加载的 30+ 秒开销。_load_model_bundle 负责带缓存的模型加载，命中/未命中日志输出到 stderr。
```

#### 实现路径

| 文件 / 函数 / 脚本 | 作用 |
|---|---|
| `b4_local_agent_llm.py::_MODEL_CACHE` (L22) | 模块级字典缓存，key 为配置元组，value 为 (tokenizer, model) |
| `b4_local_agent_llm.py::_resolve_model_profile` (L76) | 根据 routing 配置 + 阶段 + 启发式从 model_pool 选择 profile |
| `b4_local_agent_llm.py::_detect_routing_phase` (L54) | 判断路由阶段 plan/execute/direct |
| `b4_local_agent_llm.py::_classify_task_profile` (L63) | 启发式分类任务 profile (planner/default) |
| `b4_local_agent_llm.py::_load_model_bundle` (L2329) | 带缓存的模型加载（hit/miss 日志到 stderr） |
| `b4_local_agent_llm.py::_merged_model_settings` (L102) | base 配置与 profile 合并 |
| `b4_local_agent_llm.py::warmup_model` (L2676) | 模型预热入口 |

#### 演示命令

```bash
cd agent/code

# 使用 qwen_4b 生成（默认 profile）
python b4_local_agent_llm.py --model_config ../configs/model.yaml \
  --messages ../data/messages/messages_no_tool.json \
  --tools_schema ../data/messages/tools_schema_basic.json \
  --mode prompt_json --outdir ../outputs/B4_llm/no_tool_qwen4b

# 强制使用 qwen_7b 生成（通过 Module Studio 前端或 API 传入 forced_profile）
python b4_local_agent_llm.py --model_config ../configs/model.yaml \
  --messages ../data/messages/messages_no_tool.json \
  --tools_schema ../data/messages/tools_schema_basic.json \
  --mode prompt_json --forced_profile qwen_7b \
  --outdir ../outputs/B4_llm/no_tool_qwen7b
```

#### 输出格式

| 输出文件 / 返回字段 | 格式 | 说明 |
|---|---|---|
| `ai_message.json` | JSON | 标准 AIMessage，`profile_used` 字段记录实际使用的模型 profile |
| `raw_model_output.json` | JSON | 含 `profile_used` 和 `model_name` 字段，记录实际加载的模型信息 |

#### 示例图片

```text
[在此处插入模型切换运行截图]
```

示例占位：

![F3本地模型切换占位](docs/images/f3_placeholder.png)

### 5.5 进阶功能 4：F4 双模式对比

#### 功能说明

```text
F4 双模式对比：基础版本只支持 prompt_json 模式。进阶版本增加了 native_tools 模式，并实现了无感 fallback 机制和自动对比评测。

prompt_json 模式：将 tools_schema 序列化为 JSON 字符串，拼接到 system message 的 content 中。由 _build_prompt_messages 构建。兼容性最广，几乎所有开源模型都支持，但 Schema 本身占用大量 token（通常 800-1500）。

native_tools 模式：通过 tokenizer.apply_chat_template 的 tools 参数传入原生工具说明，利用模型微调时学到的特殊 token 标记工具。由 _build_native_tool_messages 构建。Token 效率更高，但依赖模型 fine-tune 程度。输出解析走 _parse_native_tool_blocks（支持 JSON payload 或 XML 格式），XML 格式为 <function=name><parameter=key>value</parameter></function>，由 _coerce_native_parameter_value 进行参数值强制类型转换（bool/int/float/null/JSON）。

Fallback 机制：generate_ai_message 中，native_tools 解析失败时（catch RuntimeError 检查 "apply_chat_template" 或 "unsupported arguments" 关键词）自动降级到 prompt_json 重试一次，不会因模型不支持就直接报错。

对比接口：compare_tools_injection_modes 可一次性用 prompt_json/native_tools/adaptive 三种模式跑同一输入，输出 comparison.json 定量对比。对比评测关键发现：qwen_4b 上 native_tools 成功率（83.3%）高于 prompt_json（66.7%），且输入 Token 节省约 22%；但 qwen_7b 上 native_tools 成功率仅为 33.3%，说明原生工具调用能力与模型版本强相关。
```

#### 实现路径

| 文件 / 函数 / 脚本 | 作用 |
|---|---|
| `b4_local_agent_llm.py::_prompt_json_generate` (L2577) | prompt_json 模式生成入口 |
| `b4_local_agent_llm.py::_native_tools_generate` (L2623) | native_tools 模式生成入口 |
| `b4_local_agent_llm.py::_build_prompt_messages` (L2373) | 构建 prompt_json 模式消息：注入 Schema、格式指令、决策策略 |
| `b4_local_agent_llm.py::_build_native_tool_messages` (L2448) | 构建 native_tools 模式消息：注入 XML 工具格式 |
| `b4_local_agent_llm.py::_parse_native_tool_blocks` (L1025) | 从原始文本提取所有 tool call 块（JSON payload 或 XML） |
| `b4_local_agent_llm.py::_parse_native_xml_tool_block` (L1003) | 解析 `<function=name><parameter=key>value</parameter></function>` XML 块 |
| `b4_local_agent_llm.py::_coerce_native_parameter_value` (L954) | 将 XML 参数值强制类型转换（bool/int/float/null/JSON） |
| `b4_local_agent_llm.py::compare_tools_injection_modes` (L3236) | 双模式对比入口，输出 comparison.json |

#### 演示命令

```bash
cd agent/code

# 单次对比：同一输入分别以 prompt_json 和 native_tools 运行
python b4_local_agent_llm.py --model_config ../configs/model.yaml \
  --messages ../data/messages/messages_tools_compare.json \
  --tools_schema ../data/messages/tools_schema_basic.json \
  --compare_tools_injection --outdir ../outputs/B3/compare_tools_injection
```

#### 输出格式

| 输出文件 / 返回字段 | 格式 | 说明 |
|---|---|---|
| `comparison.json` | JSON | 两模式对比：tool_call_count、tool_name_correct、args_complete、Token 和耗时 |

#### 示例图片

```text
[在此处插入双模式对比运行截图]
```

示例占位：

![F4双模式对比占位](docs/images/f4_placeholder.png)

### 5.6 进阶功能 5：F5 批量评估框架

#### 功能说明

```text
F5 批量评估框架：自动遍历 modes × profiles × cases 笛卡尔积组合，产出量化评估报告。

评测流程：run_batch_evaluation 遍历所有组合，逐用例调用 generate_ai_message，由 _evaluate_tool_mode_result 评估单轮结果，_summarize_eval_rows 按 profile::mode 分组计算汇总指标，_write_eval_report_csv 输出 CSV 报告。run_batch_plan_execute_evaluation 支持 Plan-and-Execute/adaptive 模式的批量评估，由 _evaluate_plan_execute_trace 从 trace 中评估工具调用正确性。

五维评估指标：
- structured_output_rate：JSON 解析稳定性——模型输出能否被正确解析
- tool_match_rate：工具选择准确性——是否选对了工具（_tool_match 支持 exact/contains 两种匹配方式）
- args_complete_rate：参数完整性——必填参数是否齐全（_required_args_map 从 tools_schema 提取）
- avg_input_tokens：Token 效率——输入 Token 越少越好
- avg_elapsed_seconds：推理速度——端到端耗时

评测用例结构：每条 case 含 id/category/expected_tools/expected_status/expected_match_type/messages 字段。lite 策略下内部工具（calculator/format_converter）可跳过校验。所有评测产物集中存放在 module_demos/outputs/b4/ 下，Module Studio 前端自动加载最新产物。
```

#### 实现路径

| 文件 / 函数 / 脚本 | 作用 |
|---|---|
| `b4_local_agent_llm.py::run_batch_evaluation` (L3474) | 单轮工具模式批量评估：遍历 modes × profiles × cases |
| `b4_local_agent_llm.py::run_batch_plan_execute_evaluation` (L3109) | Plan-and-Execute 批量评估 |
| `b4_local_agent_llm.py::_evaluate_tool_mode_result` (L2877) | 评估单轮工具结果（tool_name_correct, args_complete, token 用量） |
| `b4_local_agent_llm.py::_evaluate_plan_execute_trace` (L3028) | 从 trace 中评估工具调用正确性 |
| `b4_local_agent_llm.py::_tool_match` (L3368) | 工具名匹配（exact/contains 两种模式） |
| `b4_local_agent_llm.py::_summarize_eval_rows` (L3446) | 按 profile::mode 分组计算汇总指标 |
| `b4_local_agent_llm.py::_write_eval_report_csv` (L3414) | 写评估报告 CSV |
| `b4_local_agent_llm.py::_load_eval_cases` (L3319) | 加载并标准化 eval cases |

#### 演示命令

```bash
cd agent/code

# 批量评测：qwen_4b 和 qwen_7b × prompt_json 和 native_tools
python b4_local_agent_llm.py \
  --eval_cases ../data/messages/eval_cases_feature5.json \
  --tools_schema ../data/messages/tools_schema_basic.json \
  --batch_eval --eval_modes prompt_json,native_tools \
  --eval_profiles qwen_4b,qwen_7b \
  --model_config ../configs/model.yaml \
  --outdir ../module_demos/outputs/b4/test_b4_compat_batch_eval

# 22条端到端批量评测（Plan-and-Execute + adaptive 模式）
python b4_local_agent_llm.py \
  --eval_cases ../data/messages/eval_cases_feature5_extended.json \
  --tools_schema ../data/messages/tools_schema_basic.json \
  --tools_config ../configs/tools.yaml --toolset basic_tools \
  --batch_plan_execute --eval_modes adaptive \
  --eval_profiles qwen_4b --model_config ../configs/model.yaml \
  --max_turns 3 --max_plan_steps 6 --evidence_policy lite \
  --outdir ../module_demos/outputs/b4/verify_feature5_extended
```

#### 输出格式

| 输出文件 / 返回字段 | 格式 | 说明 |
|---|---|---|
| `eval_summary.json` | JSON | 按 `<profile>::<mode>` 分组的汇总统计（success_rate/tool_match_rate/args_complete_rate/avg_input_tokens/avg_elapsed_seconds） |
| `eval_report.csv` | CSV | 逐用例评测结果（id/category/profile/mode/success/tool_name_correct/args_complete/input_tokens/output_tokens/elapsed_seconds） |

> **评测产物位置**：所有 B4 评测结果集中在 `module_demos/outputs/b4/` 下。Module Studio 前端通过 `_load_latest_b4_eval_summary` 和 `_load_latest_b4_comparison` 自动加载最新产物。

#### 示例图片

```text
[在此处插入批量评测结果 CSV/JSON 截图]
```

示例占位：

![F5批量评估框架占位](docs/images/f5_placeholder.png)

### 5.7 扩展实现E1+E2：工具结果压缩与证据充分性校验

#### 功能说明

```text
E1 工具结果压缩：Plan-and-Execute 多步骤中 messages 越来越长，一个 10KB 的文件内容如果不截断，几步之后上下文就超出模型窗口。compress_tool_messages 作为公开入口，遍历 tool 消息逐条压缩。压缩策略按工具类型定制而非统一截断长度：
- file_reader：_compress_file_reader_output 提取 3 个要点 + 头尾截断（max_content_chars: 900）
- local_file_search：_compress_local_file_search_output 最多保留 6 个结果，每条截断（max_snippet: 260）
- table_analyzer：_compress_table_analyzer_output 限制预览行数（max_preview_rows: 6）
- 通用：_compress_text 采用 70%头部 + 尾部策略，中间用 ... 连接

E2 证据充分性校验：防 LLM"幻觉式跳步"——模型可能直接输出 STEP_DONE 声称"已读取两个文件"，但根本没调用 file_reader。_has_sufficient_evidence 作为总入口，lite 策略下跳过不需要外部证据的步骤（如"基于现有信息总结"纯推理步骤）。_step_has_sufficient_evidence 根据步骤标题中的关键词匹配对应工具的成功结果。_required_distinct_file_count 从步骤标题解析所需文件数量（支持中文数字"两篇""三个"，_cn_count_to_int 支持一~十九）。_build_file_count_shortfall_guidance 在文件数不足时生成修复指导（补搜索/ASK_USER/STEP_FAIL）。evidence_policy 分 strict/lite 两档，lite 模式下 calculator、format_converter 等内部工具跳过校验。

两者协同：E1 压缩减少上下文长度，让 E2 能在更干净的上下文中准确判断证据是否充分，长期多步骤执行中共同保证推理质量。
```

#### 实现路径

| 文件 / 函数 / 脚本 | 作用 |
|---|---|
| `b4_local_agent_llm.py::compress_tool_messages` (L686) | 公开入口：遍历 tool 消息，逐条压缩 skill result |
| `b4_local_agent_llm.py::_compress_file_reader_output` (L600) | file_reader 输出压缩：提取要点 + 头尾截断 |
| `b4_local_agent_llm.py::_compress_local_file_search_output` (L627) | local_file_search 输出压缩：限制结果数 + 截断 snippet |
| `b4_local_agent_llm.py::_compress_table_analyzer_output` (L654) | table_analyzer 输出压缩：限制预览行数 |
| `b4_local_agent_llm.py::_compress_text` (L583) | 通用文本截断压缩（70%头部+尾部） |
| `b4_local_agent_llm.py::_has_sufficient_evidence` (L1872) | 证据充分性总入口，lite 策略下跳过不需要外部证据的步骤 |
| `b4_local_agent_llm.py::_step_has_sufficient_evidence` (L1880) | 核心判断：根据步骤标题关键词匹配对应工具的成功结果 |
| `b4_local_agent_llm.py::_required_distinct_file_count` (L1787) | 从步骤标题解析所需不同文件数量（支持中文数字） |
| `b4_local_agent_llm.py::_cn_count_to_int` (L1758) | 中文数字（一~十九）转 int |
| `b4_local_agent_llm.py::_distinct_successful_file_sources` (L1804) | 从证据列表中提取所有成功 file_reader 的不同 source 路径 |
| `b4_local_agent_llm.py::_build_file_count_shortfall_guidance` (L1912) | 文件数不足时生成修复指导 |
| `b4_local_agent_llm.py::_propagate_step_evidence` (L2259) | 跨步骤证据传播 |

#### 输出格式

| 输出文件 / 返回字段 | 格式 | 说明 |
|---|---|---|
| `trace.json` | JSON | 每轮工具结果含压缩后的 content 和 evidence 校验状态 |
| `progress.md` | Markdown | 步骤状态含证据满足情况 |

### 5.8 扩展实现E3+E4：Reflexion 重规划与 Human-in-the-Loop

#### 功能说明

```text
E3 Reflexion 重规划：工具失败后简单重试无效——文件路径错了用同样错误路径重试还是失败。_replan_hint_from_tool_failures 生成结构化错误三元组（name/input/error JSON），注入 messages 引导模型"诊断→候选→选择"三步修复：
1. 诊断 1-3 个失败原因
2. 比较 1-2 个替代动作（RETRY / ASK_USER / STEP_FAIL）
3. 输出选定动作

失败信息采用结构化 JSON 而非模糊的自然语言描述，因为 LLM 对结构化信息的理解更准确，能更精确地定位失败原因。可选动作限制为三个，避免模型选择过多导致不可预测。_generate_with_retry 提供最多 3 次重试的生成包装，解析失败/空消息/缺工具时自动构建重试消息。

E4 Human-in-the-Loop：有些决策不适合 AI 自动完成——预算耗尽时继续还是停止？重复资源是故意还是失误？三种触发场景：
- 工具预算耗尽：_build_budget_exhausted_ask_user 生成 A/B/C 选项（接受现有证据/补充文件/放宽约束），分文件数不足/证据不足/纯证据驱动三种场景定制
- 重复资源请求：_duplicate_resource_confirmation_text 从模型输出中检测重复资源读取，生成 A/B/C 选项（重复处理/去重跳过/修改路径）
- 文件数不足：_build_file_count_shortfall_guidance 提示补做搜索或放宽约束

选项格式为 A/B/C 而非开放式输入，因为演示/验收场景下用户需要快速选择。但模型自主 ASK_USER 的场景保留自由文本，因为模型提出的问题无法预定义选项。

两者协同：E3 失败修复的最终手段是 ASK_USER，当 Reflexion 三次 retry 仍无法解决时，自动触发 E4 暂停等待用户决策，形成"自动修复→人工兜底"的完整容错链路。
```

#### 实现路径

| 文件 / 函数 / 脚本 | 作用 |
|---|---|
| `b4_local_agent_llm.py::_replan_hint_from_tool_failures` (L1508) | 生成结构化 Reflexion 提示（name/input/error 三元组） |
| `b4_local_agent_llm.py::_generate_with_retry` (L403) | 带重试的生成包装：最多 3 次，解析失败/空消息/缺工具时自动构建重试消息 |
| `b4_local_agent_llm.py::_tool_error_text` (L1497) | 从 error dict 或字符串中提取错误消息文本 |
| `b4_local_agent_llm.py::_is_missing_file_error` (L1503) | 判断是否为"file not found"类错误（确认不存在也算通过） |
| `b4_local_agent_llm.py::_build_budget_exhausted_ask_user` (L1949) | 工具预算耗尽时生成 ASK_USER 消息（三种场景） |
| `b4_local_agent_llm.py::_duplicate_resource_confirmation_text` (L2031) | 从模型输出中检测重复资源，生成 ASK_USER 确认请求 |
| `b4_local_agent_llm.py::_build_file_count_shortfall_guidance` (L1912) | 文件数不足时生成修复指导 |
| `b4_local_agent_llm.py::_mode_retry_instruction` (L301) | 根据模式生成重试指令文本 |

#### 输出格式

| 输出文件 / 返回字段 | 格式 | 说明 |
|---|---|---|
| `trace.json` | JSON | 每轮含 reflexion_hint（失败修复提示）和 ask_user（暂停等待的决策选项） |
| `progress.md` | Markdown | 步骤状态含 REFLEXION 修复和 ASK_USER 暂停记录 |

### 5.9 扩展实现E5+E6：自适应路由与工具结果缓存

#### 功能说明

```text
E5 自适应路由：并非所有任务都需要 Plan-and-Execute——"计算 123+456" 走多步规划反而浪费时间。采用三级路由决策：
1. 启发式快速分类：_heuristic_task_complexity 基于输入特征判定——纯算术表达式 → low（置信度 0.95）、单步文件读取 → low（0.85）、含"搜索/比较/差异"关键词 → high（0.70）、无法判断 → high（0.55）
2. LLM 分类器（可选）：classify_task_complexity 在启发式置信度不够高时调用 LLM 做精细判断，返回 {strategy, complexity, confidence, reason} JSON。LLM 分类器返回 tool_calls 而非分类结果时自动回退到启发式
3. 策略选择：_run_adaptive_execute_impl 根据分类结果，low 走 _run_react_one_round_execute_impl（单轮 ReAct 执行），high 走 Plan-and-Execute

E6 工具结果缓存：Plan-and-Execute 不同步骤可能重复读取同一文件，无缓存则同一文件被反复读取。两层去重机制：
- 第一层——发出前去重：_dedupe_identical_resource_tool_calls 基于 (name, resource_path, args_json) 签名检测本轮重复调用，只保留第一个。放在发出前是因为发出后 B3 会实际执行两次
- 第二层——跨步骤缓存：tool_result_cache 局部字典（仅在 _run_plan_execute_impl 内），key 为 name|args_json（sort_keys=True）。后续步骤请求相同参数时直接从缓存返回并构造虚拟 tool 消息，执行成功后写入缓存

两者协同：E5 自适应路由确保简单任务不走复杂流程，E6 缓存确保复杂任务中不重复执行相同工具调用，从"选对策略"和"避免浪费"两个维度共同提升系统效率。
```

#### 实现路径

| 文件 / 函数 / 脚本 | 作用 |
|---|---|
| `b4_local_agent_llm.py::classify_task_complexity` (L3596) | LLM 分类 + 启发式 fallback，返回 {strategy, complexity, confidence, reason} |
| `b4_local_agent_llm.py::_heuristic_task_complexity` (L3072) | 纯启发式分类：算术表达式=low，检索/比较/多步=high |
| `b4_local_agent_llm.py::_run_adaptive_execute_impl` (L3977) | 自适应执行核心：先分类，low 走 react_one_round，high 走 plan_execute |
| `b4_local_agent_llm.py::_run_react_one_round_execute_impl` (L3663) | ReAct 单轮执行实现（含去重/重复检测/预算管理/证据压缩） |
| `b4_local_agent_llm.py::_dedupe_identical_resource_tool_calls` (L2066) | 第一层：发出前基于 (name, resource_path, args_json) 签名去重 |
| `b4_local_agent_llm.py::tool_result_cache` (L4251) | 第二层：跨步骤缓存局部字典，key 为 name\|args_json |
| `b4_local_agent_llm.py::_build_adaptive_routing_instruction` (L3583) | 构建复杂度分类的 prompt 注入 |

#### 输出格式

| 输出文件 / 返回字段 | 格式 | 说明 |
|---|---|---|
| `trace.json` | JSON | 含 selected_mode/strategy/complexity/confidence 路由决策信息，以及 cache_hit 记录 |
| `ai_message.json` | JSON | 最终回答，含 profile_used 和路由方式 |

---

## 6. 与团队系统的集成说明

B4 在团队完整系统中的集成方式如下：

**调用入口**：B1 在每轮 Agent Loop 中调用 `b4_local_agent_llm.generate_ai_message(model_config, messages, tools_schema, mode, artifact_dir, forced_profile)`。Plan-and-Execute 和自适应执行模式通过 `b1_agent_runtime_1` 模块的 `run_plan_execute` / `run_adaptive_execute` 委托调用。

**传入参数**：B1 传入 B3 生成的 tools_schema（JSON 数组）、当前完整 messages 序列（含 system/user/assistant/tool 四种角色）、model.yaml 路径、推理模式（`prompt_json`、`native_tools` 或 `mock`）和可选的强制 profile。

**返回结果**：B4 返回 B4Result 字典，核心字段包括 `ai_message`（标准 AIMessage，含 content 或 tool_calls）、`status`（success/error）、`raw_record`（模型原始输出与解析过程）。B1 检查 `ai_message.tool_calls` 是否非空来决定是否调用 B3 执行工具。

**前端集成**：Agent Studio Web 通过 `POST /api/chat` 调用 B1 `run_agent`，B1 内部调用 B4，前端展示对话消息、执行步骤和最终回答。UI 人性化方面：server.py 内置 `_humanize_message_for_ui` 将工具调用自动翻译为自然语言描述（如"调用 file_reader 工具读取文件 xxx.md"），`_is_internal_runtime_user_message` 过滤系统内部协议消息（如 `[B1_INTERNAL_RUNTIME]`），`_merge_adjacent_assistant` 将同一个 assistant 的多条消息去重合并，提升前端展示的简洁性。模型预热通过 `_start_model_warmup` 异步加载模型 + `JOB_REGISTRY` 任务注册，前端通过 `/api/jobs` 轮询预热进度。B4 评测数据通过 `B4_FIXED_EVAL_DIRS` 映射到 `module_demos/outputs/b4/` 下的三个固定目录。

Module Studio 的 B4 演示页面通过 `POST /api/modules/b4/run` 调用 B4 的 `generate_ai_message`（真实模式）或回放已保存的 mock fixtures（mock 模式），独立展示输入输出和 raw_record。B4 评测汇总和注入对比结果通过 `/api/modules/b4/eval_summary` 和 `/api/modules/b4/comparison` 从 `module_demos/outputs/b4/` 加载最新产物。

**配置依赖**：B4 依赖 `configs/model.yaml` 中的模型路径、model_pool（四个 profile）、routing 路由策略和 generation 生成参数。不需要额外配置文件、数据集或中间文件。

**产物保存**：B4 在 `artifact_dir/llm_calls/` 下保存每次调用的 raw_model_output.json 和 ai_message.json。Plan-and-Execute 模式额外输出 plan_preview.md 和 progress.md（供前端轮询），完整系统演示通过 `run_full_demo.py` 统一输出 demo_report.md。B4 主要评测产物集中存放在 `module_demos/outputs/b4/` 目录下，包含演示输出、批量评测结果（eval_summary.json + eval_report.csv）、注入对比结果（comparison.json）和模型路由可视化数据。

**联调时遇到的接口问题与解决**：

- **AIMessage 格式不一致**：早期 B4 返回的 tool_calls 字段名不统一（`name` vs `function.name`），通过 `common/schemas.py` 统一为 `{"id", "name", "args"}` 格式，并在 `_normalize_tool_call` 中做多字段名兼容转换（从 name/args/arguments/parameters/input/function 多种来源提取）。

- **模型路径差异**：服务器和个人环境的模型路径不同，通过 `model_pool` 多 profile 配置（default/planner/qwen_4b/qwen_7b）和 `model_new.yaml` 演示配置解决。

- **native_tools 兼容性**：Qwen2.5-7B 对原生工具调用支持不稳定，通过 `generate_ai_message` 内置的 fallback 机制（native_tools 失败时 catch RuntimeError 检查 "apply_chat_template" 或 "unsupported arguments" 关键词，自动降级到 prompt_json）解决。

- **Plan-and-Execute 进度展示**：前端需要实时展示计划执行进度，使用文件轮询方案（B4 的 `_write_plan_and_progress` 写出 progress.md，前端 800ms 间隔 GET 读取），无需 WebSocket 即可实现实时进度条。

- **Agent Studio Web 对话消息可读性**：原始对话消息中包含大量系统内部协议文本（如 `[B1_INTERNAL_RUNTIME]` 标记和工具调用 JSON），直接展示对用户不友好。通过 `_humanize_message_for_ui`（将工具调用翻译为自然语言描述）、`_is_internal_runtime_user_message`（过滤协议消息）、`_merge_adjacent_assistant`（合并相邻 assistant 消息）三个函数实现 UI 人性化展示。

- **Module Studio 评测产物自动加载**：前端需要展示最新评测结果但人工指定路径不便。通过 `_find_latest_output_dir` 和 `_load_latest_b4_eval_summary` 自动扫描 `module_demos/outputs/b4/` 目录，按时间戳排序取最新产物，实现零配置自动加载。

---

## 7. 已知问题与后续改进

| 问题 | 当前原因 | 后续改进 |
|---|---|---|
| 模型路径依赖实训服务器 | `model.yaml` 使用服务器绝对路径（`/root/siton-tmp/assignment_B/`），权重未随仓库分发 | 提供环境变量覆盖和模型探测脚本，支持 `$MODEL_ROOT` 前缀替换 |
| 4B 模型复杂任务偶发格式解析偏差 | 模型能力（4B 参数规模）和结构化格式遵循能力有限，长上下文增加难度 | 优化 Prompt 与 Schema 描述，增加约束解码（constrained decoding），使用更强模型如 Qwen3.5-7B |
| native_tools 在 7B 模型上成功率低（33.3%） | Qwen2.5-7B 原生工具调用格式遵循不稳定，XML 解析容错有限 | 扩充失败用例回归集，优化 _parse_native_xml_tool_block 的容错策略，增加 native_tools 模式的 prompt 引导 |
| 真实模式资源消耗较高 | 本地 Transformers 推理依赖显存（4B 约 8GB，7B 约 14GB），首次加载和多次规划增加耗时 | 使用 GPTQ/AWQ 量化模型、启用 KV Cache 复用、模型服务化（vLLM） |
| Plan-and-Execute 多步执行耗时较长 | 每步需要一次完整 LLM 推理（规划+每步执行），22 条评测平均 21 秒 | 优化步骤间缓存复用、减少冗余上下文注入、使用 speculative decoding |
| Web 服务不适合公网部署 | 使用 Python 标准库 `http.server`（ThreadingHTTPServer），无认证和限流 | 接入正式 Web 框架（FastAPI）、添加 JWT 认证和速率限制 |
| 前端进度轮询依赖文件 I/O | 800ms 间隔轮询 progress.md，在高并发时可能产生 I/O 竞争 | 改用 Server-Sent Events（SSE）或 WebSocket 推送进度更新 |
| 证据校验对中文数字支持有限 | `_cn_count_to_int` 仅支持一~十九，复杂中文数字（如"二十三""五十"）无法解析 | 扩展中文数字解析范围，支持"零"到"九十九"的完整映射 |
| Module Studio B4 评测产物需手动运行生成 | `module_demos/outputs/b4/` 下的评测结果需在服务器端手动执行批量评测命令后更新 | 提供一键批量评测脚本，自动运行所有评测用例并输出到 `module_demos/outputs/b4/` |