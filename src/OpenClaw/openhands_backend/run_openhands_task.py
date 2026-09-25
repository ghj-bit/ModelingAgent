#!/usr/bin/env python3
"""Run one OpenHands conversation as the solver for a single evolution task.

Invoked by ``openhands_backend.run_openhands_modeling_phase`` through
``baseline.stream_command``, so everything printed here lands in the run's
``meta/solve.log`` and the process exit status is what the framework reads.

The task text is the rendered ``prompt.md`` the framework already produces; the
workspace is the task's ``output/`` directory.  The conversation runs headless
with confirmation disabled, which is the SDK default, and a watchdog interrupts
it if it overruns --timeout so a stalled model cannot wedge the phase.
"""

from __future__ import annotations

import argparse
import os
import sys
import threading
import time
from pathlib import Path

# The SDK prints an ASCII banner at import time; it would land in transport.log.
os.environ.setdefault("OPENHANDS_SUPPRESS_BANNER", "1")
# Otherwise litellm tries to fetch its model-cost map from raw.githubusercontent.com
# on every start: the request hangs for ~40s, logs warnings, and this cluster
# cannot reach GitHub anyway.  The packaged copy is enough (costs are unknown for
# a locally served model regardless).
os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")

# The prompt makes the agent run the expert-bridge helper in the *foreground*
# and block on it for up to EXPERT_REQUEST_TIMEOUT (180s).  OpenHands' terminal
# tool treats 30s of silence as a soft timeout and hands control back, which
# would leave the agent to discover that it must re-enter the wait loop with an
# empty command -- a step a 27B model fumbles, and the expert exchange is a hard
# gate.  Long computations have the same problem.  Anything above the bridge's
# own timeout keeps those commands simply "still running".
DEFAULT_NO_CHANGE_TIMEOUT_SECONDS = 1800

# Sub-agent delegation.  The OpenClaw launcher this backend replaces enables
# nested agents for the solver (it strips sessions_spawn/sessions_send/subagents
# from that CLI's tool deny-list), so a solver there can hand work to sub-agents.
# Without the ``task`` tool an OpenHands solver cannot, which would compare two
# different capability sets.  The SDK has no separate sub-agent pool: the ``task``
# tool declares no resources, so N of them in one agent step run the full N-wide
# once ``tool_concurrency_limit`` allows it.
DEFAULT_SUBAGENT_CONCURRENCY = 6

# Per-request timeout for one model call.  The solver shares the endpoint with
# the phase's other conversations (and with the expert and judge calls), so a
# request can queue behind up to --max-num-seqs others and then stream a long
# answer; a tight timeout would abort a call that is merely slow, which reads as
# a failed run and, mid-interaction, can strand an expert exchange.
DEFAULT_LLM_TIMEOUT_SECONDS = 1800.0

# The endpoint's context window, and the slice of it a request may use.  Without
# a declared input budget the SDK cannot tell when a conversation has outgrown
# the model, and a solving session -- a very large prompt, many tool calls, and
# observations up to max_message_chars each -- reliably does: the run dies with
# ContextWindowExceededError ("you requested 0 output tokens") after the input
# alone has filled the window.
CONTEXT_WINDOW_TOKENS = 131072
# Input budget + output budget must fit inside the window: the SDK condenses at
# max_input_tokens without reserving room for the reply, so the two are chosen
# to sum well under the limit and leave slack for tokenizer drift.
MAX_INPUT_TOKENS = 100000
MAX_OUTPUT_TOKENS = 16384
# Condense once the conversation passes this many events.  The agent's working
# memory (the task plan, which files it wrote) survives in the workspace and in
# the task_tracker tool, so summarising early costs little and is far cheaper
# than losing a multi-hour run at the context wall.
CONDENSER_MAX_EVENTS = 60


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt-file", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--persistence-dir", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--timeout", type=float, default=7200.0)
    parser.add_argument("--thinking", default="off")
    parser.add_argument(
        "--llm-timeout",
        type=float,
        default=DEFAULT_LLM_TIMEOUT_SECONDS,
        help="Per-request timeout for one model call.",
    )
    parser.add_argument(
        "--no-change-timeout",
        type=int,
        default=DEFAULT_NO_CHANGE_TIMEOUT_SECONDS,
        help="Seconds of terminal silence before the tool reports back.",
    )
    parser.add_argument(
        "--subagent-concurrency",
        type=int,
        default=DEFAULT_SUBAGENT_CONCURRENCY,
        help="Tool calls a single agent step may run at once (sub-agent fan-out).",
    )
    return parser.parse_args()


def litellm_model_name(model: str) -> str:
    """Route an OpenAI-compatible endpoint through litellm's ``openai/`` provider.

    The local vLLM server speaks the OpenAI protocol, but a bare model name would
    make litellm guess a provider from the name and fail.
    """
    return model if "/" in model else f"openai/{model}"


def register_preset_subagents() -> list[str]:
    """Register the SDK's preset sub-agent types for the ``task`` tool.

    Enabling the tool is not enough: without this the tool answers every call
    with "Unknown agent 'general-purpose'. Available types: none registered",
    because the presets ship as Markdown definitions that nothing loads by
    default.  Returns the names registered, for the run log.

    ``web-researcher`` is deliberately left out.  It is built on
    ``browser_tool_set``, which cannot be registered here -- the browsergym and
    playwright dependencies are absent and this is a headless cluster with no
    browser to drive -- so every delegation to it fails with "Tool
    'browser_tool_set' not registered".  Solvers reach the web through the
    terminal instead (they fetch URLs with urllib), so offering a type that can
    only fail just burns a turn; observed doing exactly that on a sand-friction
    lookup.
    """
    from openhands.sdk import (
        agent_definition_to_factory,
        load_agents_from_dir,
        register_agent,
    )
    import openhands.tools.preset as preset_package

    unavailable = {"web-researcher"}
    directory = Path(preset_package.__file__).parent / "subagents"
    if not directory.is_dir():
        return []
    registered = []
    for definition in load_agents_from_dir(directory):
        if definition.name in unavailable:
            continue
        register_agent(
            definition.name,
            agent_definition_to_factory(definition),
            definition,
        )
        registered.append(definition.name)
    return registered


def conversation_id_for(workspace: Path) -> "uuid.UUID":
    """Derive a stable conversation id from a task workspace.

    Two invocations against the same task therefore address the same stored
    conversation, which is what makes the framework's single recovery run a
    resume rather than a restart.
    """
    import uuid

    return uuid.uuid5(
        uuid.NAMESPACE_URL, f"modelingagent-openhands:{workspace.resolve()}"
    )


# The conversation's own watchdog only *interrupts* the run, and an interrupt is
# cooperative: a run wedged inside tool execution never reaches the step boundary
# that honours it (observed once, stuck in the terminal executor with no worker
# threads left).  The caller has no timeout of its own either -- stream_command
# only waits for stdout to close -- so a wedged driver would hold a whole phase
# slot forever.  This backstop guarantees the process ends and reports failure,
# which the pipeline handles by rescheduling the task.
HARD_WATCHDOG_GRACE_SECONDS = 300.0


def install_hard_watchdog(timeout: float) -> None:
    """Force the driver to exit if a run outlives its timeout plus a grace."""

    def expire() -> None:
        time.sleep(timeout + HARD_WATCHDOG_GRACE_SECONDS)
        message = (
            f"[openhands] run exceeded {timeout + HARD_WATCHDOG_GRACE_SECONDS:g}s "
            "without returning (interrupt did not take effect); forcing exit\n"
        )
        sys.stderr.write(message)
        sys.stderr.flush()
        os._exit(1)

    threading.Thread(target=expire, name="openhands-hard-watchdog", daemon=True).start()


# Thinking stays off for every OpenHands run, whatever the framework's
# ``--thinking`` level says.  The locally served model has no "off"
# reasoning_effort -- the switch is the chat template's ``enable_thinking`` --
# and its reasoning levels (xhigh/medium/low) are a different vocabulary from
# the ones the framework passes, so forwarding the flag would silently turn
# thinking back on.  Set this to False to let the framework decide again.
DISABLE_THINKING = True


def reasoning_settings(thinking: str) -> dict:
    """Return the SDK LLM options that control the model's thinking mode."""
    del thinking  # recorded in the run metadata; not forwarded to the model
    if not DISABLE_THINKING:
        return {}
    return {
        "reasoning_effort": None,
        "litellm_extra_body": {"chat_template_kwargs": {"enable_thinking": False}},
    }


def main() -> int:
    args = parse_args()
    prompt = args.prompt_file.read_text(encoding="utf-8")
    args.workspace.mkdir(parents=True, exist_ok=True)
    args.persistence_dir.mkdir(parents=True, exist_ok=True)

    # Imported here so --help works without loading the whole SDK.
    from openhands.sdk import (
        LLM,
        Agent,
        ConversationExecutionStatus,
        LLMSummarizingCondenser,
        LocalConversation,
        LocalWorkspace,
        Tool,
    )

    # Importing the package is what registers the built-in tool implementations;
    # without it the Agent fails at startup with "ToolDefinition 'terminal' is
    # not registered", since Tool(name=...) alone is only a definition.
    import openhands.tools  # noqa: F401  (side effect: registers built-in tools)

    subagent_types = register_preset_subagents()

    model = litellm_model_name(args.model)
    print(
        f"[openhands] model={model} base_url={args.base_url} "
        f"workspace={args.workspace} timeout={args.timeout:g}s "
        f"subagent_concurrency={args.subagent_concurrency} "
        f"subagent_types={subagent_types or 'none'}",
        flush=True,
    )
    llm = LLM(
        model=model,
        base_url=args.base_url,
        api_key=args.api_key,
        usage_id="solver",
        timeout=args.llm_timeout,
        num_retries=3,
        max_input_tokens=MAX_INPUT_TOKENS,
        max_output_tokens=MAX_OUTPUT_TOKENS,
        **reasoning_settings(args.thinking),
    )
    # terminal and file_editor are what the prompt's workflow needs; task_tracker
    # supports its numbered-step protocol.  The browser tool set is deliberately
    # left out: this cluster has no display and the phase would only spend
    # iterations failing to launch one.
    agent = Agent(
        llm=llm,
        tools=[
            Tool(
                name="terminal",
                params={"no_change_timeout_seconds": args.no_change_timeout},
            ),
            Tool(name="file_editor"),
            Tool(name="task_tracker"),
            # Sub-agent delegation, matching what the OpenClaw launcher enables
            # for its solvers (see DEFAULT_SUBAGENT_CONCURRENCY).  The name must
            # be the *tool set*: the SDK also registers the inner ``task`` class,
            # whose create(executor, description) signature does not match the
            # registry's create(conv_state, **params) convention and raises
            # "TaskTool.create() got an unexpected keyword argument 'conv_state'".
            Tool(name="task_tool_set"),
        ],
        # ``task`` declares no resources, so up to this many sub-agents can run
        # at once; terminal calls are additionally bounded by its pane pool.
        tool_concurrency_limit=args.subagent_concurrency,
        # Without a condenser the Agent keeps every event forever and the run
        # ends at the context wall (see MAX_INPUT_TOKENS above).
        condenser=LLMSummarizingCondenser(
            llm=llm.model_copy(update={"usage_id": "condenser"}),
            max_size=CONDENSER_MAX_EVENTS,
        ),
    )
    conversation = LocalConversation(
        agent=agent,
        workspace=LocalWorkspace(working_dir=str(args.workspace)),
        persistence_dir=str(args.persistence_dir),
        # Derived from the workspace, so the recovery run invoked by
        # run_openhands_modeling_phase resumes this same conversation instead of
        # starting over -- the OpenHands equivalent of reopening an OpenClaw
        # session.
        conversation_id=conversation_id_for(args.workspace),
        # The default rich visualizer streams the whole session to stdout, which
        # would duplicate transport.log and drown it.
        visualizer=None,
        # Keep the event log for post-mortem; the tool executors are still
        # released by close().
        delete_on_close=False,
    )

    watchdog = threading.Timer(args.timeout, conversation.interrupt)
    watchdog.daemon = True
    watchdog.start()
    install_hard_watchdog(args.timeout)
    status = ConversationExecutionStatus.IDLE
    try:
        conversation.send_message(prompt)
        conversation.run()
    finally:
        watchdog.cancel()
        status = conversation.state.execution_status
        conversation.close()

    print(f"[openhands] conversation finished with status={status}", flush=True)
    # The framework grades the run by the artifacts it finds, so a completed
    # conversation is a success even when the agent chose to stop early.  Only a
    # broken or stuck run is reported as a failure.
    if status in (ConversationExecutionStatus.ERROR, ConversationExecutionStatus.STUCK):
        print(f"[openhands] run did not complete: {status}", file=sys.stderr, flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
