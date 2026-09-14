"""Record workspace changes relative to an inherited baseline snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path


IGNORED_ROOT_FILES = {
    "AGENTS.md",
    "HEARTBEAT.md",
    "IDENTITY.md",
    "SOUL.md",
    "TOOLS.md",
    "USER.md",
    "openclaw-workspace-state.json",
}
IGNORED_FILES = {
    "code/record_refinement_changes.py",
    "code/wait_for_expert_reply.py",
    "results/baseline_workspace_manifest.json",
    "results/refinement_changed_files.json",
    "results/interaction_added_content.md",
    "results/interaction_evidence.md",
    "results/interaction_receipt.json",
    "results/refinement_validation.json",
}


def included(relative: Path) -> bool:
    value = relative.as_posix()
    return not (
        relative.parts[0] in {"logs", ".git"}
        or value == ".gitignore"
        or (len(relative.parts) == 1 and relative.name in IGNORED_ROOT_FILES)
        or value in IGNORED_FILES
    )


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def snapshot_workspace(workspace: Path) -> dict[str, dict]:
    workspace = Path(workspace).resolve()
    state = {}
    for path in sorted(workspace.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(workspace)
        if included(relative):
            state[relative.as_posix()] = {
                "sha256": digest(path),
                "size": path.stat().st_size,
            }
    return state


def write_manifest(workspace: Path, output: Path) -> dict:
    payload = {
        "generated_at": datetime.now().isoformat(),
        "workspace": str(Path(workspace).resolve()),
        "files": snapshot_workspace(workspace),
    }
    Path(output).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return payload


def write_changes(workspace: Path, manifest: Path, output: Path) -> dict:
    baseline = json.loads(Path(manifest).read_text(encoding="utf-8"))["files"]
    current = snapshot_workspace(workspace)
    baseline_names = set(baseline)
    current_names = set(current)
    payload = {
        "generated_at": datetime.now().isoformat(),
        "baseline_manifest": str(Path(manifest).resolve()),
        "modified": sorted(
            name
            for name in baseline_names & current_names
            if baseline[name]["sha256"] != current[name]["sha256"]
        ),
        "added": sorted(current_names - baseline_names),
        "deleted": sorted(baseline_names - current_names),
    }
    Path(output).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    write_changes(Path(args.workspace), Path(args.manifest), Path(args.output))


if __name__ == "__main__":
    main()
