"""Block once until the experiment controller supplies an expert reply."""

import argparse
import json
import sys
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    parser.add_argument("--reply", required=True)
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--poll-interval", type=float, default=0.2)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    request_path = Path(args.request)
    reply_path = Path(args.reply)
    deadline = time.monotonic() + args.timeout
    while time.monotonic() < deadline:
        try:
            # The Agent writes only expert_question_N.md. The controller creates
            # the fixed-schema request asynchronously, so tolerate that short
            # hand-off instead of failing a race at startup.
            if not request_path.is_file() or not request_path.read_text(
                encoding="utf-8-sig"
            ).strip():
                time.sleep(max(0.05, args.poll_interval))
                continue
            if reply_path.is_file():
                payload = json.loads(reply_path.read_text(encoding="utf-8-sig"))
                if payload.get("ok") is not True:
                    print(
                        f"Expert consultation failed: {payload.get('error', 'unknown error')}",
                        file=sys.stderr,
                    )
                    return 2
                answer = str(payload.get("answer", "")).strip()
                if answer:
                    print(answer)
                    return 0
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            # The controller writes atomically, but tolerate transient filesystem
            # visibility and antivirus/indexer races on Windows.
            pass
        time.sleep(max(0.05, args.poll_interval))

    print(
        "Timed out waiting for the controller-generated expert request/reply: "
        f"{request_path} / {reply_path}",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
