"""Pass-through shim that makes the Codex CLI usable against the served model.

Codex speaks the Responses API and so does the served endpoint, so no
translation is needed -- unlike Claude Code, which speaks Messages and needs the
full ``claude_backend/proxy.py``.  This shim exists for exactly one field.

Codex marks its own standing instructions with ``role: "developer"``.  OpenAI
treats that role as an alias of ``system``, and newer vLLM maps it, but the
deployment here is pinned to 0.19.1 (see the cluster's driver/NCCL ceiling) and
its ``/v1/responses`` rejects the role outright.  Two measurements against the
endpoint fix what the replacement has to be:

  * One ``user`` message plus the role under test: ``user``, ``system`` and
    ``assistant`` are accepted, ``developer`` answers ``Unexpected message
    role.`` -- so the role cannot survive the trip.
  * A ``system`` item inside ``input`` is only accepted when nothing else
    precedes it, and Codex always sets the top-level ``instructions`` field,
    which occupies that slot.  Renaming the item to ``system`` therefore just
    moves the failure: ``System message must be at the beginning.``

So the developer text cannot stay in ``input`` at all.  It is folded into
``instructions``, which is where the Responses API carries developer-level
instructions in the first place, and which this endpoint does accept.

Every other byte of the request and of the response is relayed untouched,
including the SSE stream, so this adds no behaviour of its own to reason about.
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DEVELOPER_ROLE = "developer"
# The conversation is carried under one of these, depending on the caller.
CONVERSATION_KEYS = ("input", "messages")

# A Codex turn legitimately runs long: the solver writes and executes a
# modelling pipeline, and the endpoint streams tokens for minutes at a time.
UPSTREAM_TIMEOUT = 3600


class UpstreamRejected(Exception):
    """The upstream refused the request before any response body existed."""


def extract_text(content) -> str:
    """Flatten a Responses-API content value to its text."""
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts = []
    for part in content:
        if isinstance(part, dict) and isinstance(part.get("text"), str):
            parts.append(part["text"])
    return "\n".join(parts)


def move_developer_instructions(body: dict) -> int:
    """Fold every developer-role item into ``instructions``, in place.

    Returns how many items moved, so the shim can say whether it did anything
    rather than leaving the reader to guess.  The item is removed from the
    conversation rather than relabelled -- see the module docstring for the two
    measurements that rule out every relabelling.
    """
    for key in CONVERSATION_KEYS:
        items = body.get(key)
        if not isinstance(items, list):
            continue
        kept, texts = [], []
        for item in items:
            if isinstance(item, dict) and item.get("role") == DEVELOPER_ROLE:
                texts.append(extract_text(item.get("content")))
            else:
                kept.append(item)
        if not texts:
            return 0
        body[key] = kept
        existing = body.get("instructions")
        parts = [existing] if isinstance(existing, str) and existing.strip() else []
        parts.extend(text for text in texts if text.strip())
        body["instructions"] = "\n\n".join(parts)
        return len(texts)
    return 0


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    upstream = ""  # base URL of the served endpoint, e.g. http://host:8000/v1
    api_key = ""
    # One line per shim process, so a run log answers "did the rewrite fire?"
    # without needing the request captured separately.
    _logged_first_rewrite = False

    def log_message(self, *args) -> None:  # keep the run log readable
        pass

    def _write_chunk(self, data: bytes) -> None:
        self.wfile.write(b"%x\r\n%s\r\n" % (len(data), data))
        self.wfile.flush()

    def _send_error(self, status: int, message: str) -> None:
        body = json.dumps(
            {"error": {"message": message, "type": "api_error", "param": None, "code": status}}
        ).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _upstream_headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        # "EMPTY" is this repo's sentinel for "this endpoint wants no
        # credentials", so it must not become a bearer token.
        if self.api_key and self.api_key != "EMPTY":
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _target_url(self) -> str:
        """Join the upstream base with the request path without doubling ``/v1``.

        ``--upstream`` is an OpenAI-compatible base URL and it ends in ``/v1``.
        Codex is pointed at this shim the same way, so its requests arrive as
        ``/v1/responses``; appending that verbatim would ask the server for
        ``/v1/v1/responses``.  One of the two prefixes has to go, and it is
        cheaper to drop it here than to make the caller remember which.
        """
        path = self.path
        if self.upstream.endswith("/v1") and path.startswith("/v1/"):
            path = path[len("/v1"):]
        return self.upstream + path

    def _relay(self, method: str, body: bytes | None) -> None:
        """Send one request upstream and stream the response back as chunked.

        Chunked framing is used for every response, streaming or not: it keeps
        the relay byte-for-byte and avoids re-computing a length the upstream
        already decided.
        """
        request = urllib.request.Request(
            self._target_url(),
            data=body,
            headers=self._upstream_headers(),
            method=method,
        )
        try:
            response = urllib.request.urlopen(request, timeout=UPSTREAM_TIMEOUT)
        except urllib.error.HTTPError as error:
            # Relay the rejection verbatim: the CLI reports the server's own
            # message, which is what makes the next failure diagnosable.
            response = error
        except (urllib.error.URLError, OSError) as error:
            self._send_error(502, f"upstream unreachable: {error}")
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
        finally:
            response.close()

    def do_GET(self) -> None:
        self._relay("GET", None)

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

        moved = move_developer_instructions(body)
        if moved and not Handler._logged_first_rewrite:
            Handler._logged_first_rewrite = True
            sys.stderr.write(
                f"[shim] folded {moved} developer-role item(s) into instructions\n"
            )
            sys.stderr.flush()
        # Re-serialise only when something changed, so an unrelated POST keeps
        # its exact bytes.
        payload = json.dumps(body).encode("utf-8") if moved else raw
        self._relay("POST", payload)


class Server(ThreadingHTTPServer):
    """A server that does not traceback when a client disconnects mid-stream.

    Codex closes the SSE stream as soon as it has what it needs, which surfaces
    in the worker thread as ConnectionResetError/BrokenPipeError.  That is the
    normal end of a turn rather than a fault, and one traceback per turn would
    bury the rewrite line this shim exists to print.
    """

    daemon_threads = True

    def handle_error(self, request, client_address) -> None:
        error = sys.exc_info()[1]
        if isinstance(error, (ConnectionResetError, BrokenPipeError)):
            return
        super().handle_error(request, client_address)


def free_port() -> int:
    """Reserve a port by binding it, then release it for the shim to claim."""
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--upstream", required=True, help="base URL, e.g. http://host:8000/v1"
    )
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--api-key", default="", help="bearer token; empty when none")
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    Handler.upstream = args.upstream.rstrip("/")
    Handler.api_key = args.api_key
    sys.stderr.write(f"[shim] {args.host}:{args.port} -> {Handler.upstream}\n")
    sys.stderr.flush()
    Server((args.host, args.port), Handler).serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
