"""Block once until the experiment controller supplies an expert reply."""

import argparse
import itertools
import json
import re
import sys
import time
from pathlib import Path

# The handshake is bounded far below the 180 s this used to wait.  Measured on
# claude_fp8_keepframe_r10 round_0: the controller picks the question up in
# 0.004-0.03 s and the expert answers in 1.0-1.7 s, so the whole exchange costs
# about two seconds.  70 s is still ~40x the observed latency, and it is a hard
# cap rather than only a default: prompts rendered before this change carry
# `--timeout 180` as a literal, and those runs must not be able to wait it out.
MAX_TIMEOUT_SECONDS = 70.0

# How long to tolerate a question that has not appeared yet before diagnosing
# why.  The documented order is "write the question, then run this script", so
# this only has to cover the write landing; the poll below sees it in 0.2 s.
# It is not zero because the two steps are separate tool calls, and a solve that
# starts the wait a moment early is not the failure this is looking for.
DIAGNOSE_AFTER_SECONDS = 15.0

# Bound on the wrong-directory search, so a misconfigured path cannot turn this
# into a filesystem walk.
MAX_STRAY_CANDIDATES = 500


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    parser.add_argument("--reply", required=True)
    parser.add_argument("--timeout", type=float, default=MAX_TIMEOUT_SECONDS)
    parser.add_argument("--poll-interval", type=float, default=0.2)
    # Exposed so the diagnosis below can be exercised without a 15 s sleep.
    parser.add_argument("--diagnose-after", type=float, default=DIAGNOSE_AFTER_SECONDS)
    # How many exchanges the policy allows.  0 means "not stated", and a run that
    # does not pass it gets the reply alone -- this script is shared with arms
    # whose solver prompt never asks for an operator heading.
    parser.add_argument("--exchanges", type=int, default=0)
    return parser.parse_args()


def effective_timeout(requested: float) -> float:
    """The requested timeout, capped.

    A cap rather than only a default because the solver prompt renders the value
    as a literal: prompts emitted before the cap existed still say
    `--timeout 180`, and those runs must not be able to wait it out.
    """
    return min(float(requested), MAX_TIMEOUT_SECONDS)


def question_for_request(request_path: Path) -> Path | None:
    """The `expert_question_<N>.md` the controller pairs with this request.

    The controller watches for the question and writes the request in response,
    so an absent request plus an absent question is one symptom, not two.
    """
    match = re.search(r"(\d+)$", request_path.stem)
    if not match:
        return None
    return request_path.with_name(f"expert_question_{match.group(1)}.md")


def misplaced_question(question_path: Path) -> Path | None:
    """Find the same question written where the controller does not read it.

    This is the failure the diagnosis exists for: the solver writes
    `<output>/logs/expert_question_1.md` while the controller only ever reads
    `<output>/logs/operator_feedback/expert_question_1.md`.  Nothing rejects the
    write, the request is never created, and the run used to burn its whole
    timeout and then fail without saying why -- three minutes and six solver
    heartbeats on the run that prompted this.  Naming both paths turns that into
    an immediate, actionable error.

    The search is deliberately narrow -- one directory up from the feedback
    directory -- because the point is to recognise the mistake, not to hunt for
    it.
    """
    if len(question_path.parents) < 2:
        return None
    root = question_path.parents[1]
    try:
        if not root.is_dir():
            return None
        for found in itertools.islice(root.rglob(question_path.name), MAX_STRAY_CANDIDATES):
            if found != question_path:
                return found
    except OSError:
        return None
    return None


def diagnose_missing_question(request_path: Path) -> str | None:
    """Why the request has not appeared, phrased for the solver to act on."""
    question = question_for_request(request_path)
    if question is None:
        return None
    if question.is_file():
        # The question is where it belongs, so the controller is simply slow.
        return None
    stray = misplaced_question(question)
    if stray is not None:
        return (
            f"The expert question was written to {stray}, but the controller "
            f"only reads {question}. Move it there and run this command again."
        )
    return (
        f"No expert question at {question}. The controller creates the request "
        f"only after that file exists, so it will never arrive. Write the "
        f"question there and run this command again."
    )



def exchange_number(request_path: Path) -> int:
    """The exchange this request belongs to, read off `expert_request_<N>.json`."""
    match = re.search(r"(\d+)\s*$", request_path.stem)
    return int(match.group(1)) if match else 0


def next_exchange_reminder(number: int, total: int) -> str:
    """The line appended to a reply that still has an exchange after it.

    The reply is the last thing read before the next question is written, so it
    is where the reminder that an exchange is still owed has to sit; the policy
    states the budget once, at the top, and by the third exchange that is a long
    way up the context.
    """
    return (
        "\n---\n"
        f"[controller] Exchange {number} of {total} recorded. "
        f"Has this conversation ended?  Ignore the rest.\n"
        f"If you are about to ask again: write the next question to "
        f"`expert_question_{number + 1}.md` and run the same command against "
        f"`expert_request_{number + 1}.json` and `expert_reply_{number + 1}.json`. "
        f"Build it on the reply above.\n"
    )


def main() -> int:
    args = parse_args()
    request_path = Path(args.request)
    reply_path = Path(args.reply)
    timeout = effective_timeout(args.timeout)
    if timeout < args.timeout:
        print(
            f"[controller] --timeout {args.timeout:.0f}s is above the "
            f"{MAX_TIMEOUT_SECONDS:.0f}s handshake cap; waiting {timeout:.0f}s.",
            file=sys.stderr,
        )
    started = time.monotonic()
    deadline = started + timeout
    diagnosed = False
    while time.monotonic() < deadline:
        try:
            # The Agent writes only expert_question_N.md. The controller creates
            # the fixed-schema request asynchronously, so tolerate that short
            # hand-off instead of failing a race at startup.
            if not request_path.is_file() or not request_path.read_text(
                encoding="utf-8-sig"
            ).strip():
                # The request is derived from the question, so once the hand-off
                # window has passed, a request that never arrives is a question
                # the controller cannot see -- say which, rather than waiting out
                # the cap and failing with no explanation.
                if (
                    not diagnosed
                    and time.monotonic() - started >= args.diagnose_after
                ):
                    diagnosed = True
                    reason = diagnose_missing_question(request_path)
                    if reason is not None:
                        print(reason, file=sys.stderr)
                        return 2
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
                    number = exchange_number(request_path)
                    if 0 < number < args.exchanges:
                        print(next_exchange_reminder(number, args.exchanges))
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
