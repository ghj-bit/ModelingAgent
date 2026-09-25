#!/usr/bin/env python3
"""Anthropic-to-OpenAI translation shim for the Claude Code solver.

Claude Code speaks the Anthropic Messages API, and the local vLLM server exposes
one -- but that endpoint cannot run this workload, so this process translates to
the OpenAI shape the server handles properly.  Measured on vllm 0.19.1 serving
Qwen3.8-27B, two independent problems rule out the direct connection:

1. The served Qwen template emits a reasoning block on every request, and the
   Anthropic endpoint offers no way to stop it.  ``thinking: {"type": "disabled"}``
   is not a field of the request model, and ``chat_template_kwargs`` is not
   either; pydantic drops both silently, so requests succeed while the model
   still spends its budget thinking.  The OpenAI endpoint does honour a
   per-request ``chat_template_kwargs``, which is why this shim talks OpenAI
   rather than passing the Anthropic body through.

2. Claude Code puts the system prompt in ``messages`` as ``{"role": "system"}``,
   which the Anthropic endpoint rejects with HTTP 400 -- it accepts only ``user``
   and ``assistant`` there.

Run as ``python proxy.py --upstream http://host:port/v1 --port N --model NAME``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Anthropic stop reasons, which Claude Code matches on.  A tool call must report
# tool_use or the client will not run the tools it was just handed.
STOP_REASONS = {
    "stop": "end_turn",
    "length": "max_tokens",
    "tool_calls": "tool_use",
    "function_call": "tool_use",
    "content_filter": "end_turn",
}

# Generous, but below the server's 131072-token window: Claude Code asks for
# large budgets and the model may spend several thousand tokens before answering.
MAX_OUTPUT_TOKENS = 32768

# The server rejects a request whose prompt plus requested output exceeds the
# window, and the rejection names both numbers.  Reading them back is how the
# output budget gets shrunk to fit.
CONTEXT_REJECTION = re.compile(
    r"maximum context length is (\d+) tokens.*?at least (\d+) input tokens",
    re.S,
)
# Headroom kept when re-fitting the output budget against a measured prompt.
CONTEXT_MARGIN = 1024
# Below this there is no useful answer left to ask for, so the error is passed
# through rather than retried into a truncated one.
MIN_OUTPUT_TOKENS = 256


class UpstreamRejected(Exception):
    """The endpoint refused the request and no adaptation was possible."""


def context_window(detail: str) -> int | None:
    """The model's window, as named in the rejection."""
    match = CONTEXT_REJECTION.search(detail)
    return int(match.group(1)) if match else None


def shrink_to_fit(
    payload: dict, detail: str, prompt_tokens: int | None = None
) -> dict | None:
    """Return the payload with an output budget that fits the window, or None.

    Claude Code asks for a fixed 32k output tokens however much of the context
    it has already used, and it sizes its own auto-compaction against a 200k
    window while this server serves 131072.  The two together push a long
    session over the limit, and the server refuses the whole turn -- which the
    client reports as an API error and abandons.  One retry with a budget that
    fits keeps the turn alive and costs only the discarded prefill.

    ``prompt_tokens`` must be the prompt's real length, measured separately.
    The number in the rejection is NOT it: the message reads "your prompt
    contains at least N input tokens" where N is ``window - requested_output +
    1``, a value derived from the request rather than measured.  Sizing the
    retry against it reproduces the same rejection -- measured: a 129k prompt
    rejected with "at least 99073", retried at 15999, rejected again.
    """
    window = context_window(detail)
    if window is not None and prompt_tokens:
        room = window - prompt_tokens - CONTEXT_MARGIN
    else:
        # No measurement and no usable window: halve what was asked for and
        # let the next rejection, if any, halve it again.
        current = payload.get("max_tokens")
        room = (current // 2) if isinstance(current, int) else 0
    if room < MIN_OUTPUT_TOKENS:
        return None
    requested = payload.get("max_tokens")
    if isinstance(requested, int) and requested <= room:
        return None  # already fits, so this rejection is about something else
    fitted = dict(payload)
    fitted["max_tokens"] = room
    return fitted


def as_text(value) -> str:
    """Flatten string-or-content-blocks into plain text."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "".join(as_text(item) for item in value)
    if isinstance(value, dict):
        return value.get("text") if isinstance(value.get("text"), str) else ""
    return ""


def convert_tools(tools) -> list:
    """Anthropic tool declarations to OpenAI function declarations."""
    converted = []
    for tool in tools or []:
        if not isinstance(tool, dict):
            continue
        function = {"name": tool.get("name") or ""}
        if tool.get("description"):
            function["description"] = tool["description"]
        schema = tool.get("input_schema")
        function["parameters"] = (
            schema if isinstance(schema, dict) else {"type": "object", "properties": {}}
        )
        converted.append({"type": "function", "function": function})
    return converted


def convert_tool_choice(choice):
    """Anthropic tool_choice to its OpenAI equivalent."""
    if not isinstance(choice, dict):
        return None
    kind = choice.get("type")
    if kind == "auto":
        return "auto"
    if kind == "any":
        return "required"
    if kind == "none":
        return "none"
    if kind == "tool":
        return {"type": "function", "function": {"name": choice.get("name") or ""}}
    return None


def to_openai(body: dict, model: str) -> dict:
    """Rewrite an Anthropic Messages request as an OpenAI chat completion."""
    # A leading system turn belongs in the system prompt -- the endpoint rejects
    # it inside messages, and the OpenAI shape has a dedicated field for it.
    # System turns that appear later, mid-conversation, have no OpenAI
    # equivalent and ride along as user text in the loop below.
    leading_system = []
    conversation = []
    seen_conversation = False
    for item in body.get("messages") or []:
        is_system = isinstance(item, dict) and item.get("role") == "system"
        if is_system and not seen_conversation:
            leading_system.append(as_text(item.get("content")))
        else:
            seen_conversation = seen_conversation or not is_system
            conversation.append(item)

    messages = []
    system = "\n\n".join(
        part for part in [as_text(body.get("system")), *leading_system] if part.strip()
    )
    if system.strip():
        messages.append({"role": "system", "content": system})

    for item in conversation:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if role not in ("user", "assistant"):
            role = "user"
        if isinstance(content, str):
            if content.strip():
                messages.append({"role": role, "content": content})
            continue
        if not isinstance(content, list):
            continue

        texts, tool_calls, tool_results = [], [], []
        for block in content:
            if not isinstance(block, dict):
                continue
            kind = block.get("type")
            if kind == "text":
                texts.append(block.get("text") or "")
            elif kind == "tool_use":
                tool_calls.append(
                    {
                        "id": block.get("id") or f"call_{uuid.uuid4().hex[:24]}",
                        "type": "function",
                        "function": {
                            "name": block.get("name") or "",
                            "arguments": json.dumps(
                                block.get("input") or {}, ensure_ascii=False
                            ),
                        },
                    }
                )
            elif kind == "tool_result":
                tool_results.append(
                    {
                        "role": "tool",
                        "tool_call_id": block.get("tool_use_id") or "",
                        "content": as_text(block.get("content")) or "(no output)",
                    }
                )
            # thinking / redacted_thinking have no OpenAI equivalent and the
            # template is asked not to produce them; images are not used by
            # this workflow, so both are dropped.

        text = "\n".join(part for part in texts if part.strip())
        if role == "assistant":
            if not text and not tool_calls:
                continue
            message = {"role": "assistant", "content": text or None}
            if tool_calls:
                message["tool_calls"] = tool_calls
            messages.append(message)
        else:
            # A tool result must directly follow the assistant turn that asked
            # for it, so these go before any accompanying user text.
            messages.extend(tool_results)
            if text.strip():
                messages.append({"role": "user", "content": text})

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": min(int(body.get("max_tokens") or 4096), MAX_OUTPUT_TOKENS),
        # The only working switch for the template's thinking mode.  The
        # Anthropic request model has no field for it, so it is injected here.
        "chat_template_kwargs": {"enable_thinking": False},
    }
    for name in ("temperature", "top_p"):
        if isinstance(body.get(name), (int, float)):
            payload[name] = body[name]
    if body.get("top_k") is not None:
        payload["top_k"] = body["top_k"]
    if body.get("stop_sequences"):
        payload["stop"] = body["stop_sequences"]
    tools = convert_tools(body.get("tools"))
    if tools:
        payload["tools"] = tools
        choice = convert_tool_choice(body.get("tool_choice"))
        if choice is not None:
            payload["tool_choice"] = choice
    if body.get("stream"):
        payload["stream"] = True
    return payload


def from_openai(body: dict, model: str) -> dict:
    """Rewrite an OpenAI chat completion as an Anthropic Messages response."""
    choice = (body.get("choices") or [{}])[0]
    message = choice.get("message") or {}
    content = []
    text = message.get("content")
    if isinstance(text, str) and text.strip():
        content.append({"type": "text", "text": text})
    for call in message.get("tool_calls") or []:
        if not isinstance(call, dict):
            continue
        function = call.get("function") or {}
        raw = function.get("arguments")
        try:
            arguments = json.loads(raw) if raw else {}
        except ValueError:
            # The API requires an object; keep the text rather than fail the turn.
            arguments = {"_raw": raw}
        if not isinstance(arguments, dict):
            arguments = {"value": arguments}
        content.append(
            {
                "type": "tool_use",
                "id": call.get("id") or f"toolu_{uuid.uuid4().hex[:24]}",
                "name": function.get("name") or "",
                "input": arguments,
            }
        )
    if not content:
        content.append({"type": "text", "text": ""})

    usage = body.get("usage") or {}
    stop_reason = STOP_REASONS.get(choice.get("finish_reason"), "end_turn")
    if any(block["type"] == "tool_use" for block in content):
        stop_reason = "tool_use"
    return {
        "id": body.get("id") or f"msg_{uuid.uuid4().hex[:24]}",
        "type": "message",
        "role": "assistant",
        "model": model,
        "content": content,
        "stop_reason": stop_reason,
        "stop_sequence": None,
        "usage": {
            "input_tokens": usage.get("prompt_tokens") or 0,
            "output_tokens": usage.get("completion_tokens") or 0,
        },
    }


class StreamTranslator:
    """Rebuild the Anthropic event sequence from an OpenAI SSE stream.

    Claude Code reads the Anthropic shape, so deltas have to be re-framed:
    message_start, then content_block_start / *_delta / content_block_stop per
    block, then message_delta and message_stop.
    """

    def __init__(self, model: str):
        self.model = model
        self.message_id = f"msg_{uuid.uuid4().hex[:24]}"
        self.index = -1
        self.kind = None  # None, "text" or "tool_use"
        self.tool_slots: dict[int, dict] = {}
        self.input_tokens = 0
        self.output_tokens = 0
        self.stop_reason = "end_turn"
        self.emitted = False

    @staticmethod
    def event(name: str, payload: dict) -> bytes:
        line = json.dumps(payload, ensure_ascii=False)
        return f"event: {name}\ndata: {line}\n\n".encode("utf-8")

    def start(self) -> bytes:
        return self.event(
            "message_start",
            {
                "type": "message_start",
                "message": {
                    "id": self.message_id,
                    "type": "message",
                    "role": "assistant",
                    "model": self.model,
                    "content": [],
                    "stop_reason": None,
                    "stop_sequence": None,
                    "usage": {"input_tokens": 0, "output_tokens": 0},
                },
            },
        )

    def _close(self) -> bytes:
        if self.kind is None:
            return b""
        self.kind = None
        return self.event(
            "content_block_stop",
            {"type": "content_block_stop", "index": self.index},
        )

    def _open(self, kind: str, block: dict) -> bytes:
        self.index += 1
        self.kind = kind
        self.emitted = True
        return self.event(
            "content_block_start",
            {"type": "content_block_start", "index": self.index, "content_block": block},
        )

    def _delta(self, delta: dict, index: int) -> bytes:
        return self.event(
            "content_block_delta",
            {"type": "content_block_delta", "index": index, "delta": delta},
        )

    def _open_tool(self, state: dict) -> bytes:
        """Open a tool_use block and replay whatever fragments arrived early.

        The block's name is fixed at content_block_start and cannot be patched
        afterwards, so the block is held back until the name is known.
        """
        out = self._close()
        state["block"] = self.index + 1
        out += self._open(
            "tool_use",
            {
                "type": "tool_use",
                "id": state["id"],
                "name": state["name"],
                "input": {},
            },
        )
        for fragment in state["arguments"]:
            out += self._delta(
                {"type": "input_json_delta", "partial_json": fragment},
                state["block"],
            )
        state["arguments"] = []
        return out

    def feed(self, delta: dict) -> bytes:
        out = b""
        # A reasoning delta is dropped rather than forwarded; if the template
        # ignores enable_thinking it must not reach the client as content.
        text = delta.get("content")
        if isinstance(text, str) and text:
            if self.kind != "text":
                out += self._close() + self._open("text", {"type": "text", "text": ""})
            out += self._delta({"type": "text_delta", "text": text}, self.index)

        for call in delta.get("tool_calls") or []:
            if not isinstance(call, dict):
                continue
            slot = call.get("index")
            slot = slot if isinstance(slot, int) else 0
            function = call.get("function") or {}
            state = self.tool_slots.setdefault(
                slot,
                {"block": None, "id": f"toolu_{uuid.uuid4().hex[:24]}", "name": "", "arguments": []},
            )
            if call.get("id"):
                state["id"] = call["id"]
            if function.get("name"):
                state["name"] += function["name"]
            if function.get("arguments"):
                state["arguments"].append(function["arguments"])
            if state["block"] is None and state["name"]:
                out += self._open_tool(state)
            elif state["block"] is not None and state["arguments"]:
                for fragment in state["arguments"]:
                    out += self._delta(
                        {"type": "input_json_delta", "partial_json": fragment},
                        state["block"],
                    )
                state["arguments"] = []
        return out

    def finish(self) -> bytes:
        out = self._close()
        # A turn that produced nothing still needs one block; the API does not
        # accept an empty content array.
        if not self.emitted:
            out += self._open("text", {"type": "text", "text": ""})
            out += self._close()
        stop_reason = "tool_use" if self.tool_slots else self.stop_reason
        out += self.event(
            "message_delta",
            {
                "type": "message_delta",
                "delta": {"stop_reason": stop_reason, "stop_sequence": None},
                "usage": {
                    "input_tokens": self.input_tokens,
                    "output_tokens": self.output_tokens,
                },
            },
        )
        out += self.event("message_stop", {"type": "message_stop"})
        return out


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    upstream = ""  # OpenAI base URL, e.g. http://host:port/v1
    model = ""
    # Bearer token for the upstream.  The local server authenticates nothing, so
    # this stays empty for it; an endpoint reached over the network (DeepSeek)
    # answers 401 without one.
    api_key = ""
    # One line per shim process recording what the client asked to generate.
    # It is the only way to see whether CLAUDE_CODE_MAX_OUTPUT_TOKENS is being
    # honoured, and the requested budget is what sets the prompt ceiling.
    _logged_first_request = False

    def log_message(self, *args) -> None:  # keep the run log readable
        pass

    def _write_chunk(self, data: bytes) -> None:
        try:
            self.wfile.write(b"%x\r\n%s\r\n" % (len(data), data))
            self.wfile.flush()
        except OSError:
            raise

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status: int, message: str) -> None:
        self._send_json(
            status, {"type": "error", "error": {"type": "api_error", "message": message}}
        )

    def _upstream_headers(self) -> dict:
        """Headers for a call to the upstream, credentials included when set."""
        headers = {"Content-Type": "application/json"}
        # "EMPTY" is this repo's sentinel for "this endpoint wants no credentials"
        # -- the local server, which is what every arm but the DeepSeek one talks
        # to -- so it must not turn into a bearer token.
        if self.api_key and self.api_key != "EMPTY":
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _proxy_binary(self, method: str, body: bytes | None = None) -> None:
        """Relay a request unchanged, re-framing the response as chunked."""
        request = urllib.request.Request(
            self.upstream + self.path,
            data=body,
            headers=self._upstream_headers(),
            method=method,
        )
        try:
            response = urllib.request.urlopen(request, timeout=3600)
        except urllib.error.HTTPError as error:
            response = error
        except urllib.error.URLError as error:
            self._send_error(502, f"upstream unreachable: {error.reason}")
            return
        self.send_response(response.status)
        for key, value in response.headers.items():
            if key.lower() in ("transfer-encoding", "connection", "content-length"):
                continue
            self.send_header(key, value)
        self.send_header("Transfer-Encoding", "chunked")
        self.end_headers()
        try:
            while True:
                chunk = response.read(8192)
                if not chunk:
                    break
                self._write_chunk(chunk)
            self._write_chunk(b"")
        except OSError:
            pass

    def do_GET(self) -> None:
        self._proxy_binary("GET")

    def do_POST(self) -> None:
        raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        path = self.path.split("?")[0].rstrip("/")
        try:
            body = json.loads(raw) if raw else {}
        except ValueError:
            self._send_error(400, "request body is not JSON")
            return
        if not isinstance(body, dict):
            self._send_error(400, "request body must be a JSON object")
            return

        if path.endswith("/messages/count_tokens"):
            self._count_tokens(body)
        elif path.endswith("/messages"):
            if not Handler._logged_first_request:
                Handler._logged_first_request = True
                sys.stderr.write(
                    f"[shim] first request asks for max_tokens={body.get('max_tokens')}\n"
                )
                sys.stderr.flush()
            if body.get("stream"):
                self._stream(body)
            else:
                self._complete(body)
        else:
            self._proxy_binary("POST", raw)

    def _count_tokens(self, body: dict) -> None:
        """Answer Anthropic's token-count probe from the server's own template.

        Claude Code uses this for context accounting, so it only has to be
        close; the character estimate is the fallback if rendering fails.
        """
        payload = to_openai(body, self.model)
        count = self._prompt_tokens(payload)
        if not isinstance(count, int):
            count = sum(
                len(str(message.get("content") or ""))
                for message in payload["messages"]
            ) // 4
        self._send_json(200, {"input_tokens": count})

    def _post(self, payload: dict):
        request = urllib.request.Request(
            self.upstream + "/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=self._upstream_headers(),
            method="POST",
        )
        return urllib.request.urlopen(request, timeout=3600)

    def _prompt_tokens(self, payload: dict) -> int | None:
        """Measure the prompt exactly, through the server's own template.

        Needed because the rejection message does not report it -- see
        shrink_to_fit.  A budget fitted to the wrong number simply reproduces
        the rejection, so this measurement is what makes the retry work.

        There is no /tokenize on this server.  /chat/completions/render does
        exist: it applies the same chat template the completion would and
        returns the resulting token ids, so their length is exactly the number
        the window check will compare against.

        Render is vLLM's, not part of the OpenAI API -- an endpoint reached over
        the network answers 404 there, which is why the failure below returns
        None rather than raising: the caller falls back to halving the output
        budget, which needs no measurement.
        """
        # Must mirror the completion request, tools included: their JSON schemas
        # are several thousand tokens, and a count that omits them understates
        # the prompt by exactly that much.  Measured consequence: a prompt
        # counted at 100717 was then rejected with 20000 output requested, and
        # the retry was skipped as "already fits" -- the undercount had made the
        # remaining room look larger than it was.  Render applies the same chat
        # template, so with the same fields its token ids are the same ones the
        # window check will count.
        body = {"model": self.model, "messages": payload["messages"]}
        for key in ("tools", "tool_choice"):
            if payload.get(key) is not None:
                body[key] = payload[key]
        request = urllib.request.Request(
            self.upstream + "/chat/completions/render",
            data=json.dumps(body).encode("utf-8"),
            headers=self._upstream_headers(),
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                token_ids = json.loads(response.read().decode("utf-8")).get("token_ids")
        except (urllib.error.URLError, ValueError, OSError):
            return None
        return len(token_ids) if isinstance(token_ids, list) and token_ids else None

    def _open_upstream(self, payload: dict):
        """Post the request, re-fitting the output budget once if nothing fits."""
        try:
            return self._post(payload)
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", "replace")
            measured = self._prompt_tokens(payload)
            fitted = shrink_to_fit(payload, detail, measured)
            if fitted is None:
                # Logged because a silent skip is indistinguishable from the
                # handler never running, which is exactly the ambiguity that
                # made the first real failure hard to read.
                sys.stderr.write(
                    f"[shim] window full but not retryable: prompt={measured} "
                    f"window={context_window(detail)} requested="
                    f"{payload.get('max_tokens')}\n"
                )
                sys.stderr.flush()
                raise UpstreamRejected(f"{error.code}: {detail[:600]}") from None
            sys.stderr.write(
                f"[shim] window full; prompt={measured} tokens; retrying with "
                f"max_tokens={fitted['max_tokens']} (was {payload.get('max_tokens')})\n"
            )
            sys.stderr.flush()
            try:
                return self._post(fitted)
            except urllib.error.HTTPError as retry_error:
                raise UpstreamRejected(
                    f"{retry_error.code}: "
                    f"{retry_error.read().decode('utf-8', 'replace')[:600]}"
                ) from None

    def _complete(self, body: dict) -> None:
        payload = to_openai(body, self.model)
        try:
            with self._open_upstream(payload) as response:
                result = json.loads(response.read().decode("utf-8"))
        except UpstreamRejected as error:
            self._send_error(502, f"upstream rejected the request: {error}")
            return
        except (urllib.error.URLError, ValueError, OSError) as error:
            self._send_error(502, f"upstream call failed: {error}")
            return
        self._send_json(200, from_openai(result, self.model))

    def _stream(self, body: dict) -> None:
        payload = to_openai(body, self.model)
        translator = StreamTranslator(self.model)
        try:
            response = self._open_upstream(payload)
        except UpstreamRejected as error:
            self._send_error(502, f"upstream rejected the request: {error}")
            return
        except (urllib.error.URLError, OSError) as error:
            self._send_error(502, f"upstream call failed: {error}")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Transfer-Encoding", "chunked")
        self.end_headers()
        try:
            self._write_chunk(translator.start())
            for line in response:
                line = line.decode("utf-8", "replace").strip()
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    event = json.loads(data)
                except ValueError:
                    continue
                usage = event.get("usage") or {}
                if usage:
                    translator.input_tokens = usage.get("prompt_tokens") or translator.input_tokens
                    translator.output_tokens = (
                        usage.get("completion_tokens") or translator.output_tokens
                    )
                choices = event.get("choices") or []
                if not choices:
                    continue
                choice = choices[0]
                chunk = translator.feed(choice.get("delta") or {})
                if chunk:
                    self._write_chunk(chunk)
                if choice.get("finish_reason"):
                    translator.stop_reason = STOP_REASONS.get(
                        choice["finish_reason"], "end_turn"
                    )
            self._write_chunk(translator.finish())
            self._write_chunk(b"")
        except OSError:
            pass
        finally:
            response.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", required=True, help="OpenAI base URL, e.g. http://host:8000/v1")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--model", required=True, help="model name to send upstream")
    parser.add_argument(
        "--api-key",
        default="",
        help="bearer token for the upstream; leave empty when it wants none",
    )
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    Handler.upstream = args.upstream.rstrip("/")
    Handler.model = args.model
    Handler.api_key = args.api_key
    sys.stderr.write(f"[shim] {args.host}:{args.port} -> {Handler.upstream} model={args.model}\n")
    sys.stderr.flush()
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
