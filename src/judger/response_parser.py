"""Robust parsing for JSON objects returned by Judge models."""

import ast
import json
import re


def _balanced_objects(text: str) -> list[str]:
    objects = []
    start = None
    depth = 0
    quote = None
    escaped = False
    for index, char in enumerate(text):
        if quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if depth and char in ('"', "'"):
            quote = char
        elif char == "{":
            if depth == 0:
                start = index
            depth += 1
        elif char == "}" and depth:
            depth -= 1
            if depth == 0 and start is not None:
                objects.append(text[start : index + 1])
                start = None
    return objects


def parse_json_object(content: str) -> dict:
    """Parse a Judge response without requiring a fenced JSON block."""
    if not isinstance(content, str) or not content.strip():
        raise ValueError("Judge returned an empty response")

    candidates = [
        match.group(1).strip()
        for match in re.finditer(
            r"```(?:json)?\s*(.*?)```", content, flags=re.IGNORECASE | re.DOTALL
        )
    ]
    candidates.append(content.strip())
    candidates.extend(
        sorted(_balanced_objects(content), key=len, reverse=True)
    )

    errors = []
    for candidate in candidates:
        if not candidate:
            continue
        for parser in (json.loads, ast.literal_eval):
            try:
                result = parser(candidate)
            except (ValueError, SyntaxError, json.JSONDecodeError) as error:
                errors.append(str(error))
                continue
            if isinstance(result, dict):
                return result
    detail = errors[-1] if errors else "no JSON object found"
    raise ValueError(f"Could not parse Judge response as a JSON object: {detail}")
