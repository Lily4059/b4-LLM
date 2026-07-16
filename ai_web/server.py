from __future__ import annotations

import json
import sys
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


AI_WEB_DIR = Path(__file__).resolve().parent
AGENT_DIR = AI_WEB_DIR.parent
STATIC_DIR = AI_WEB_DIR / "static"
OUTPUTS_DIR = AGENT_DIR / "outputs" / "web_ui"

sys.path.insert(0, str(AGENT_DIR / "code"))


def _json_response(handler: SimpleHTTPRequestHandler, payload: object, status: int = 200) -> None:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def _error(handler: SimpleHTTPRequestHandler, status: int, message: str, *, details: object | None = None) -> None:
    payload: dict[str, object] = {"status": "error", "message": message}
    if details is not None:
        payload["details"] = details
    _json_response(handler, payload, status=status)


def _read_json_body(handler: SimpleHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length", "0") or "0")
    if length <= 0:
        return {}
    raw = handler.rfile.read(length)
    if not raw:
        return {}
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("request body must be a JSON object")
    return value


def _now_tag() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def _latest_trace_dir() -> Path | None:
    marker = OUTPUTS_DIR / ".latest_run.json"
    if not marker.exists():
        return None
    try:
        payload = json.loads(marker.read_text(encoding="utf-8"))
    except Exception:
        return None
    path = payload.get("path") if isinstance(payload, dict) else None
    if not isinstance(path, str):
        return None
    candidate = Path(path)
    return candidate if candidate.exists() else None


def _set_latest_trace_dir(path: Path) -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUTS_DIR / ".latest_run.json").write_text(
        json.dumps({"path": str(path)}, ensure_ascii=False),
        encoding="utf-8",
    )


class AgentStudioHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            self._handle_api_get(parsed)
            return
        if parsed.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if not parsed.path.startswith("/api/"):
            self.send_error(404)
            return
        self._handle_api_post(parsed)

    def _handle_api_get(self, parsed) -> None:
        query = parse_qs(parsed.query or "")
        try:
            if parsed.path == "/api/status":
                self._api_status()
                return
            if parsed.path == "/api/tools":
                toolset = (query.get("toolset") or ["basic_tools"])[0]
                auto_from_code = (query.get("auto_from_code") or ["0"])[0] in {"1", "true", "yes"}
                self._api_tools(toolset, auto_from_code)
                return
            if parsed.path == "/api/memory/index":
                self._api_memory_index()
                return
            if parsed.path == "/api/trace/latest":
                self._api_trace_latest()
                return
            if parsed.path == "/api/config/model":
                self._api_model_config()
                return
        except Exception as exc:
            _error(self, 500, f"{type(exc).__name__}: {exc}")
            return
        _error(self, 404, "unknown api endpoint")

    def _handle_api_post(self, parsed) -> None:
        try:
            if parsed.path == "/api/chat":
                self._api_chat()
                return
            if parsed.path == "/api/memory/search":
                self._api_memory_search()
                return
        except Exception as exc:
            _error(self, 500, f"{type(exc).__name__}: {exc}")
            return
        _error(self, 404, "unknown api endpoint")

    def _api_status(self) -> None:
        from common.io_utils import read_yaml

        tools_config = read_yaml(AGENT_DIR / "configs" / "tools.yaml") or {}
        model_config = read_yaml(AGENT_DIR / "configs" / "model.yaml") or {}
        toolsets = list((tools_config.get("toolsets") or {}).keys()) if isinstance(tools_config, dict) else []
        models = list((model_config.get("models") or {}).keys()) if isinstance(model_config, dict) else []
        payload = {
            "status": "ok",
            "agent_root": str(AGENT_DIR),
            "toolsets": toolsets,
            "models": models,
            "default_toolset": tools_config.get("default_toolset"),
            "default_mode": (model_config.get("runtime") or {}).get("default_mode") if isinstance(model_config, dict) else None,
        }
        _json_response(self, payload)

    def _api_tools(self, toolset: str, auto_from_code: bool) -> None:
        from b3_tool_layer import get_tools_schema

        schema = get_tools_schema(
            str(AGENT_DIR / "configs" / "tools.yaml"),
            toolset,
            outdir=None,
            auto_from_code=auto_from_code,
        )
        _json_response(self, {"status": "ok", "toolset": toolset, "schema": schema})

    def _api_memory_index(self) -> None:
        from b5_memory import _memory_paths, _read_index

        paths = _memory_paths(str(AGENT_DIR / "configs" / "memory.yaml"))
        index = _read_index(paths["index"])
        _json_response(self, {"status": "ok", "index": index})

    def _api_memory_search(self) -> None:
        from b5_memory import VECTOR_DIMENSIONS, _memory_paths, _read_index, _search_by_keywords, _search_by_vectors

        body = _read_json_body(self)
        query = (body.get("query") or "").strip()
        mode = (body.get("mode") or "keyword").strip()
        top_k = body.get("top_k") or 5
        if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k <= 0:
            raise ValueError("top_k must be a positive integer")

        paths = _memory_paths(str(AGENT_DIR / "configs" / "memory.yaml"))
        index = _read_index(paths["index"])

        if mode == "vector":
            results = _search_by_vectors(index, query, paths["root"], top_k=top_k)
            _json_response(self, {"status": "ok", "mode": "vector", "dimensions": VECTOR_DIMENSIONS, "results": results})
            return

        results = _search_by_keywords(index, query, paths["root"], top_k=top_k)
        _json_response(self, {"status": "ok", "mode": "keyword", "results": results})

    def _api_model_config(self) -> None:
        from common.io_utils import read_yaml

        config = read_yaml(AGENT_DIR / "configs" / "model.yaml")
        _json_response(self, {"status": "ok", "config": config})

    def _api_chat(self) -> None:
        from b1_agent_runtime import run_agent

        body = _read_json_body(self)
        user_input = (body.get("user_input") or "").strip()
        if not user_input:
            raise ValueError("user_input is required")

        conversation_id = (body.get("conversation_id") or f"conv_web_{_now_tag()}").strip()
        toolset = (body.get("toolset") or "basic_tools").strip()
        llm_mode = body.get("llm_mode")
        if llm_mode is not None and llm_mode not in {"mock", "prompt_json", "native_tools", "adaptive"}:
            raise ValueError("llm_mode must be one of: mock, prompt_json, native_tools, adaptive")

        selected_memory_ids = body.get("selected_memory_ids") or []
        if not isinstance(selected_memory_ids, list) or not all(isinstance(item, str) for item in selected_memory_ids):
            raise ValueError("selected_memory_ids must be a list of strings")

        use_global_memory = body.get("use_global_memory")
        if use_global_memory is None:
            use_global_memory = True
        if not isinstance(use_global_memory, bool):
            raise ValueError("use_global_memory must be boolean")

        max_turns = body.get("max_turns")
        if max_turns is None:
            max_turns = 3
        if not isinstance(max_turns, int) or isinstance(max_turns, bool) or max_turns <= 0:
            raise ValueError("max_turns must be a positive integer")

        save_memory = body.get("save_memory")
        if save_memory is None:
            save_memory = "none"
        if save_memory not in {"none", "conversation", "global"}:
            raise ValueError("save_memory must be none, conversation, or global")

        run_dir = OUTPUTS_DIR / conversation_id / _now_tag()
        run_dir.mkdir(parents=True, exist_ok=True)

        runtime_input = {
            "conversation_id": conversation_id,
            "user_input": user_input,
            "system_prompt_path": str((AGENT_DIR / "prompts" / "local_tool_agent.txt").resolve()),
            "selected_memory_ids": selected_memory_ids,
            "use_global_memory": use_global_memory,
            "toolset": toolset,
            "max_turns": max_turns,
            "save_memory": save_memory,
        }

        input_path = run_dir / "runtime_input.json"
        input_path.write_text(json.dumps(runtime_input, ensure_ascii=False, indent=2), encoding="utf-8")

        result = run_agent(
            str(input_path),
            str(AGENT_DIR / "configs" / "tools.yaml"),
            str(AGENT_DIR / "configs" / "memory.yaml"),
            str(AGENT_DIR / "configs" / "model.yaml"),
            str(run_dir),
            llm_mode,
        )

        messages = json.loads(Path(result["messages_path"]).read_text(encoding="utf-8"))
        trace = json.loads(Path(result["trace_path"]).read_text(encoding="utf-8"))

        _set_latest_trace_dir(run_dir)

        payload = {
            "status": "ok",
            "conversation_id": result["conversation_id"],
            "execution_mode": result["execution_mode"],
            "run_dir": str(run_dir),
            "final_answer": result["final_answer"],
            "elapsed_ms": result["elapsed_ms"],
            "messages": messages,
            "trace": trace,
            "selected_memory": result.get("selected_memory"),
            "saved_memory": result.get("saved_memory"),
        }
        _json_response(self, payload)

    def _api_trace_latest(self) -> None:
        latest_dir = _latest_trace_dir()
        if latest_dir is None:
            _json_response(self, {"status": "ok", "exists": False})
            return
        trace_path = latest_dir / "trace.json"
        messages_path = latest_dir / "messages.json"
        if not trace_path.exists():
            _json_response(self, {"status": "ok", "exists": False})
            return
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        messages = json.loads(messages_path.read_text(encoding="utf-8")) if messages_path.exists() else []
        _json_response(self, {"status": "ok", "exists": True, "run_dir": str(latest_dir), "trace": trace, "messages": messages})


def main(argv: list[str] | None = None) -> int:
    """Launch the enhanced Agent Studio implementation from the stable entry point."""
    from server_1 import main as enhanced_main

    return enhanced_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
