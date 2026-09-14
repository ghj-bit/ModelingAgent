# MM-Agent + OpenClaw baseline

This baseline turns the broad MM-Agent problem-solving pattern into a natural-language OpenClaw skill adapted to ModelingBench. The workflow lives in the repository-root `prompt.md`, and the runner is `run_mm_agent_baseline.py`.

The skill covers the full execution path: understand the problem, design an overall approach, decompose dependent subtasks, solve them in order, integrate results, validate the solution, and write the final report. It intentionally omits MM-Agent implementation names, source-code calls, and MM-Agent hyperparameters. The current problem determines the decomposition and modeling detail.

Run from the ModelingAgent repository root:

```powershell
# Prepare the rendered prompt and installed skill without calling OpenClaw or Judge
python -m src.OpenClaw.run_mm_agent_baseline 2013_Bank_Service_Problem --prepare-only

# Solve and evaluate one problem
python -m src.OpenClaw.run_mm_agent_baseline 2013_Bank_Service_Problem

# Solve without evaluation
python -m src.OpenClaw.run_mm_agent_baseline 2013_Bank_Service_Problem --skip-judge

# Run selected problems, each in its own workspace
python -m src.OpenClaw.run_mm_agent_baseline 2013_Bank_Service_Problem 2025_Managing_Sustainable_Tourism --skip-judge
```

Replace the example ID with the desired ModelingBench problem ID. Use `--all` for the full benchmark. For a single problem with attachments, pass `--data-dir PATH`; those files are copied into the installed skill workspace.

Each run contains the rendered `prompt.md`, `output/skills/mm-agent-pipeline/SKILL.md`, intermediate files created by OpenClaw, and `output/results/solution_report.md`. The runner submits only the final report through the existing ModelingBench judge path. `--prepare-only` records the run as prepared rather than solved.

The workflow is prompt-driven. The runner prepares the workspace, invokes OpenClaw, checks for a non-empty final report, and optionally evaluates it; it does not enforce every intermediate reasoning step as a programmatic state machine.

Validate locally with:

```powershell
python -m unittest discover -s tests -p test_mm_agent_openclaw_baseline.py
```
