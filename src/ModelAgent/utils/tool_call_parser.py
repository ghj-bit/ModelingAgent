import ast
import json
import re
import uuid
from types import SimpleNamespace
from typing import Any, List

PYTHON_TAG_RE = re.compile(r"<\|python_tag\|>", re.S)
JSON_BLOCK_RE = re.compile(r"```json", re.S | re.I)


def _extract_balanced_json(text: str):
    """
    Return the first balanced {...} or [...] JSON substring in text, or None.

    The old non-greedy regexes broke on nested objects (e.g.
    {"name": "multi_tools_executor", "parameters": {...}}), stopping at the
    first closing brace. Brace counting handles nesting and string literals.
    """
    pairs = {"{": "}", "[": "]"}
    start, open_ch = -1, None
    for ch in ("{", "["):
        idx = text.find(ch)
        if idx >= 0 and (start < 0 or idx < start):
            start, open_ch = idx, ch
    if start < 0:
        return None

    close_ch = pairs[open_ch]
    depth = 0
    in_str = False
    escape = False
    for i in range(start, len(text)):
        c = text[i]
        if in_str:
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == '"':
                in_str = False
            continue
        if c == '"':
            in_str = True
        elif c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return None

def _to_dict(obj: Any) -> dict:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "dict"):
        return obj.dict()
    if isinstance(obj, dict):
        return obj
    return {"content": str(obj)}

def _to_ns(d: dict) -> SimpleNamespace:
    """Convert True/False/None to valid JSON; remove trailing commas and other common issues"""
    if isinstance(d, dict):
        return SimpleNamespace(**{k: _to_ns(v) for k, v in d.items()})
    if isinstance(d, list):
        return [_to_ns(i) for i in d]
    return d

def _fix_json(text: str) -> str:
    rep = [
        (r"\bTrue\b",  "true"),
        (r"\bFalse\b", "false"),
        (r"\bNone\b",  "null"),
        (r",\s*([}\]])", r"\1")
    ]
    for pat, repl in rep:
        text = re.sub(pat, repl, text)
    return text


def parse_json_arguments(value: Any) -> dict:
    """Parse tool arguments while tolerating common LLM JSON mistakes."""
    if isinstance(value, dict):
        return value
    if value is None or not isinstance(value, str):
        raise ValueError("Tool arguments must be a JSON object or string")

    text = value.strip()
    candidates = [text, _fix_json(text)]

    # LaTeX commands such as \mu are invalid JSON escapes when emitted raw.
    escaped = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', candidates[-1])
    candidates.append(escaped)

    # Some compatible APIs return JavaScript-like objects with bare keys.
    quoted_keys = re.sub(
        r'([{,]\s*)([A-Za-z_][A-Za-z0-9_-]*)(\s*:)',
        r'\1"\2"\3',
        escaped,
    )
    candidates.append(quoted_keys)

    last_error = None
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
            if not isinstance(parsed, dict):
                raise ValueError("Tool arguments must decode to a JSON object")
            return parsed
        except (json.JSONDecodeError, ValueError) as exc:
            last_error = exc

    # ast.literal_eval safely covers single-quoted Python-style dictionaries.
    python_style = re.sub(r"\btrue\b", "True", _fix_json(text), flags=re.I)
    python_style = re.sub(r"\bfalse\b", "False", python_style, flags=re.I)
    python_style = re.sub(r"\bnull\b", "None", python_style, flags=re.I)
    try:
        parsed = ast.literal_eval(python_style)
        if isinstance(parsed, dict):
            return parsed
    except (SyntaxError, ValueError):
        pass

    raise ValueError(f"Invalid tool-call JSON: {last_error}") from last_error

def _build_tool_call(name: str, arguments: dict, call_id: str | None = None):
    return {
        "id": call_id or f"call_{uuid.uuid4().hex[:8]}",
        "type": "function",
        "function": {
            "name": name,
            "arguments": json.dumps(arguments, ensure_ascii=False)
        }
    }

def extract_tool_call(message: Any):
    """
    Parse assistant message, return *new* SimpleNamespace:
    - If already contains function_call/tool_calls → directly normalize and return
    - Otherwise try to parse <|python_tag|> / ```json``` code blocks from content
    - If both fail ⇒ return original message
    """
    msg_dict = _to_dict(message)

    if fc := msg_dict.get("function_call"):
        tool = _build_tool_call(fc.get("name"), parse_json_arguments(fc.get("arguments", "{}")))
        return _to_ns({"role": "assistant", "content": None, "tool_calls": [tool]})

    if msg_dict.get("tool_calls"):
        return _to_ns(msg_dict)

    content: str = msg_dict.get("content") or ""
    if not content:
        return message

    json_txt = None
    if PYTHON_TAG_RE.search(content):
        json_txt = _extract_balanced_json(content.split("<|python_tag|>", 1)[1])
    elif JSON_BLOCK_RE.search(content):
        block = content.split("```json", 1)[1].split("```", 1)[0]
        json_txt = _extract_balanced_json(block)
    if json_txt is None:
        return message

    json_txt = _fix_json(json_txt.strip())
    try:
        payload = json.loads(json_txt)
    except json.JSONDecodeError:
        return message

    # Allow payload to be directly a list/single item
    calls: List[dict] = []
    if isinstance(payload, list):
        for p in payload:
            calls.append(
                _build_tool_call(p.get("name"), p.get("parameters", {}), p.get("id"))
            )
    else:
        calls.append(
            _build_tool_call(payload.get("name"),
                             payload.get("parameters", {}),
                             payload.get("id"))
        )

    return _to_ns({"role": "assistant", "content": None, "tool_calls": calls})
