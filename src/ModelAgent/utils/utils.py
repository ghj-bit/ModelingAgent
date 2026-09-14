import json
import re


def form_message(system, user):
    return [
        {
            "role": "system",
            "content": system
        },
        {
            "role": "user",
            "content": user
        }
    ]


def _balanced_json_substring(candidate: str):
    """Return the first balanced {...} or [...] substring of ``candidate``.

    Brace counting is string-literal aware, so braces/quotes inside JSON string
    values do not terminate the scan early. Returns None when no balanced
    substring exists.
    """
    pairs = {"{": "}", "[": "]"}
    start, open_ch = -1, None
    for ch in ("{", "["):
        idx = candidate.find(ch)
        if idx >= 0 and (start < 0 or idx < start):
            start, open_ch = idx, ch
    if start < 0:
        return None

    close_ch = pairs[open_ch]
    depth = 0
    in_str = False
    escape = False
    for i in range(start, len(candidate)):
        c = candidate[i]
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
                return candidate[start:i + 1]
    return None


def _repair_json_candidates(raw: str):
    """Yield progressively repaired variants of a JSON string."""
    yield raw
    # Common LLM mistakes: Python-style booleans/null and trailing commas.
    fixed = re.sub(r"\bTrue\b", "true", raw)
    fixed = re.sub(r"\bFalse\b", "false", fixed)
    fixed = re.sub(r"\bNone\b", "null", fixed)
    fixed = re.sub(r",\s*([}\]])", r"\1", fixed)
    yield fixed
    # LaTeX backslashes (\mu, \lambda, \rho) are invalid JSON escapes. Escape
    # ONLY invalid ones, keeping valid escapes (\", \\, \n, ...) intact —
    # doubling every backslash would corrupt valid escapes and create new
    # parse errors. The negative lookbehind keeps the second backslash of an
    # already-escaped pair untouched.
    yield re.sub(r'(?<!\\)\\(?!["\\/bfnrtu])', r"\\\\", fixed)


def extract_json(text):
    """Robustly extract the first JSON object/array from an LLM response.

    Handles markdown code fences, preambles and trailing text, and repairs
    common LLM JSON mistakes (trailing commas, True/False/None, unescaped
    LaTeX backslashes). Raises ``ValueError`` when no valid JSON is present
    instead of silently returning a string (which previously caused
    "string indices must be integers").
    """
    text = text.strip()

    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    candidate = fenced.group(1).strip() if fenced else text

    raw = _balanced_json_substring(candidate)
    if raw is None:
        raise ValueError("No valid JSON found in response")

    last_error = None
    for fixed in _repair_json_candidates(raw):
        try:
            return json.loads(fixed)
        except json.JSONDecodeError as exc:
            last_error = exc

    raise ValueError(f"Could not parse JSON from response: {last_error}")


def execute_json(core, messages, max_retries=3):
    """Call ``core.execute`` and parse the response as JSON.

    On parse failure, feeds the error back to the model and retries, so a
    single malformed response cannot kill a long pipeline run.

    Returns ``(parsed, last_response)``.
    """
    last_response = ""
    last_error = None
    msgs = list(messages)
    for attempt in range(max_retries):
        last_response = core.execute(msgs)
        try:
            return extract_json(last_response), last_response
        except ValueError as exc:
            last_error = exc
            print(f"[utils] JSON parse failed (attempt {attempt + 1}/{max_retries}): {exc}")
            msgs = msgs + [{
                "role": "user",
                "content": (
                    "Your previous response could not be parsed as JSON. "
                    f"Error: {exc}. Please output ONLY valid JSON (no markdown "
                    "fences, no trailing commas, no comments, no extra text), "
                    "and nothing else."
                ),
            }]
    raise ValueError(
        f"JSON parsing failed after {max_retries} attempts. Last error: {last_error}"
    )
