import json
import os
import shutil
import traceback

from src.ModelAgent.engines.simulation import SimulationAgent
from src.ModelAgent.utils.tool_call_parser import parse_json_arguments


class RefinementSimulationAgent(SimulationAgent):
    """A bounded simulation workflow built from complete refinement attempts.

    Each group runs at most three rounds with up to five attempts per round.
    Every attempt generates solution and validation code, executes both, and
    feeds their outputs into the next attempt. The first attempt whose solution
    and validation both execute successfully completes the group immediately.
    """

    MAX_ROUNDS = 3
    ATTEMPTS_PER_ROUND = 3
    SOLUTION_PATH = "experiments/simulation.py"
    VALIDATION_PATH = "experiments/validate_simulation.py"
    SHARED_DIR_NAME = "shared"

    ATTEMPT_SCHEMA = [
        {
            "name": "submit_simulation_attempt",
            "description": (
                "Submit one complete simulation refinement attempt, including "
                "the main executable solution and its executable validation."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "thinking": {
                        "type": "string",
                        "description": "Briefly explain how this attempt improves the previous one.",
                    },
                    "solution_code": {
                        "type": "string",
                        "description": (
                            "Complete standalone Python solution. It must run in the group "
                            "workspace, save quantitative artifacts, and create or update "
                            "results/report.md from actual computed results."
                        ),
                    },
                    "validation_code": {
                        "type": "string",
                        "description": (
                            "Complete standalone Python validation program. It must inspect "
                            "the solution artifacts, test numerical or logical invariants, "
                            "print useful diagnostics, and exit nonzero when validation fails."
                        ),
                    },
                },
                "required": ["thinking", "solution_code", "validation_code"],
            },
        }
    ]

    def _attempt_prompt(
        self,
        *,
        group_suffix,
        round_index,
        attempt_index,
        previous_code,
        previous_result,
    ):
        factors_key = self.task_table[group_suffix]["factors_key"]
        factors = self.context_dict.get(factors_key, [])
        history_key = self.task_table[group_suffix].get("history_key")
        modeling_history = self.context_dict.get(history_key, []) if history_key else []
        latest_model = modeling_history[-1] if modeling_history else {}
        latest_model_text = json.dumps(latest_model, ensure_ascii=False, indent=2)
        if len(latest_model_text) > 16000:
            latest_model_text = latest_model_text[-16000:]
        question = self.context_dict.get("question", "")
        modeling_question = self.context_dict.get("modeling_question", question)
        expert_advice = self.context_dict.get("expert_advice")

        refinement = "This is the first attempt; build a sound baseline."
        if previous_code:
            refinement = (
                "Refine the previous solution below. Preserve correct parts and make "
                "concrete changes based on its execution and validation results.\n\n"
                f"PREVIOUS SOLUTION CODE:\n```python\n{previous_code[-24000:]}\n```\n\n"
                f"PREVIOUS ATTEMPT RESULT:\n{previous_result[-8000:]}"
            )

        advice = ""
        if expert_advice:
            advice += (
                "\n\nEXPERT CONSULTATION ADVICE:\n"
                + json.dumps(expert_advice, ensure_ascii=False, indent=2)[-8000:]
            )

        system = (
            "You are a mathematical-modeling simulation engineer. Follow this tool-call "
            "contract exactly:\n"
            "1. Call only submit_simulation_attempt. Do not call file_writer_tool, "
            "python_execution_tool, file_lister_tool, or any other tool directly.\n"
            "2. Pass exactly these top-level arguments: thinking, solution_code, and "
            "validation_code. Do not use use_tool or tool_params wrappers.\n"
            "3. Put raw, complete Python source in solution_code and validation_code; "
            "do not wrap either value in Markdown code fences.\n"
            "4. Keep solution_code under 16000 characters and validation_code under "
            "8000 characters. Prefer concise reusable functions over long narration.\n"
            "5. Keep internal reasoning brief and submit the function call promptly so "
            "the output budget is reserved for the two code fields.\n"
            "6. Every text file read or write in generated Python must explicitly use "
            "encoding='utf-8' (and CSV writes should also set newline='').\n"
            "The agent will write and execute both files after your function call. "
            "Produce complete replacements, not patches. The main code must perform "
            "meaningful model computation, emit reproducible quantitative outputs, and "
            "write results/report.md. The validation code must independently inspect "
            "generated artifacts and fail with an assertion or nonzero exit when checks "
            "do not pass."
        )
        user = f"""# Mathematical Modeling Task

## Original Question
{question}

## Modeling Question
{modeling_question}

## Factors for Group {group_suffix}
{json.dumps(factors, ensure_ascii=False, indent=2)}

## Latest Refined Model for Group {group_suffix}
{latest_model_text}

## Progress
Round {round_index}/{self.MAX_ROUNDS}, attempt {attempt_index}/{self.ATTEMPTS_PER_ROUND}.
{refinement}{advice}

Use paths relative to the current workspace. Do not install packages or request user input.
"""
        return [{"role": "system", "content": system}, {"role": "user", "content": user}]

    @staticmethod
    def _extract_attempt(response):
        message = response.choices[0].message
        tool_calls = getattr(message, "tool_calls", None) or []
        for tool_call in tool_calls:
            if tool_call.function.name != "submit_simulation_attempt":
                continue
            args = parse_json_arguments(tool_call.function.arguments)
            solution_code = args.get("solution_code")
            validation_code = args.get("validation_code")
            if not isinstance(solution_code, str) or not solution_code.strip():
                raise ValueError("solution_code is empty")
            if not isinstance(validation_code, str) or not validation_code.strip():
                raise ValueError("validation_code is empty")
            return solution_code, validation_code, args.get("thinking", "")
        finish_reason = getattr(response.choices[0], "finish_reason", None)
        reasoning = RefinementSimulationAgent._reasoning_content(message) or ""
        content = getattr(message, "content", None) or ""
        raise ValueError(
            "submit_simulation_attempt tool call was not returned "
            f"(finish_reason={finish_reason}, reasoning_chars={len(reasoning)}, "
            f"content_chars={len(content)})"
        )

    def _write_and_execute(self, file_path, code):
        call = {
            "file_writer_tool": {
                "use_tool": True,
                "tool_params": {
                    "file_path": file_path,
                    "content": code,
                    "mode": "w",
                },
            },
            "python_execution_tool": {
                "use_tool": True,
                "tool_params": {"file_path": file_path},
            },
        }
        return self.tool_handler.handle_call(
            call,
            data_point=None,
            context_path=self.sim_context_path,
        )

    @staticmethod
    def _execution_result(tool_output):
        results = tool_output.get("tool_results", {})
        write_result = results.get("file_writer_tool") or {}
        run_result = results.get("python_execution_tool") or {}
        success = bool(write_result.get("success") and run_result.get("success"))
        return success, str(run_result.get("message", "No execution output"))

    def _run_attempt(self, *, group_suffix, round_index, attempt_index,
                     previous_code, previous_result):
        messages = self._attempt_prompt(
            group_suffix=group_suffix,
            round_index=round_index,
            attempt_index=attempt_index,
            previous_code=previous_code,
            previous_result=previous_result,
        )
        response = self._call_llm_with_tools(
            messages,
            self.ATTEMPT_SCHEMA,
            tool_choice="auto",
            thinking="enabled",
        )
        solution_code, validation_code, thinking = self._extract_attempt(response)

        solution_output = self._write_and_execute(self.SOLUTION_PATH, solution_code)
        solution_ok, solution_message = self._execution_result(solution_output)

        validation_output = self._write_and_execute(self.VALIDATION_PATH, validation_code)
        validation_ok, validation_message = self._execution_result(validation_output)

        global_attempt = (
            (round_index - 1) * self.ATTEMPTS_PER_ROUND + attempt_index - 1
        )
        combined = {
            "finish": False,
            "summary": (
                f"Round {round_index} attempt {attempt_index}: generated, executed, "
                f"and validated code; solution_ok={solution_ok}, "
                f"validation_ok={validation_ok}"
            ),
            "tool_results": {
                "solution": solution_output.get("tool_results", {}),
                "validation": validation_output.get("tool_results", {}),
            },
        }
        self._append_sim_history_entry(
            global_attempt,
            {
                "round": round_index,
                "attempt": attempt_index,
                "thinking": thinking,
                "solution_path": self.SOLUTION_PATH,
                "validation_path": self.VALIDATION_PATH,
            },
            combined,
        )
        self._record_modeling_history(
            group_suffix, global_attempt, "Python_Execution_Tool", combined
        )

        result_text = (
            f"solution_success={solution_ok}\n"
            f"solution_output:\n{solution_message}\n\n"
            f"validation_success={validation_ok}\n"
            f"validation_output:\n{validation_message}"
        )
        self._log_print(
            "tool",
            f"Round {round_index}/{self.MAX_ROUNDS}, attempt "
            f"{attempt_index}/{self.ATTEMPTS_PER_ROUND}: "
            f"solution_ok={solution_ok}, validation_ok={validation_ok}",
        )
        return solution_code, result_text, solution_ok and validation_ok

    def single_modeling_run(self, group_suffix: str, max_iter=None, first_attempt=True):
        if group_suffix not in self.group_paths:
            return {
                "success": False,
                "score": 0,
                "iterations": 0,
                "group": group_suffix,
                "error": "Group not found",
            }

        self.current_group_suffix = group_suffix
        grp_root = self.group_paths[group_suffix]["root"]
        for name in ("data", "model", "experiments", "results"):
            os.makedirs(os.path.join(grp_root, name), exist_ok=True)

        os.environ["WORKSPACE_PATH"] = grp_root
        previous_directory = os.getcwd()
        self.sim_context_path = os.path.join(grp_root, "context.json")
        self.sim_history_path = os.path.join(grp_root, "simulation_history.txt")
        if not os.path.exists(self.sim_context_path):
            self._save_json(self.sim_context_path, {})
        self._init_sim_history_file()

        solution_path = os.path.join(grp_root, self.SOLUTION_PATH)
        previous_code = ""
        if os.path.exists(solution_path):
            with open(solution_path, "r", encoding="utf-8") as file:
                previous_code = file.read()
        previous_result = (
            "Continue refining the existing workspace implementation."
            if previous_code
            else ""
        )
        group_context = self._load_json(self.sim_context_path)
        checkpoint = group_context.get("refinement_checkpoint", {})
        attempts_completed = min(
            max(int(checkpoint.get("attempts_completed", 0)), 0),
            self.MAX_ROUNDS * self.ATTEMPTS_PER_ROUND,
        )
        if checkpoint.get("previous_result"):
            previous_result = checkpoint["previous_result"]
        validation_passed = checkpoint.get("validation_passed") is True
        passed_round = checkpoint.get("round") if validation_passed else None
        passed_attempt = checkpoint.get("attempt") if validation_passed else None

        try:
            os.chdir(grp_root)
            self._log_print(
                "system",
                f"Refinement simulation for group {group_suffix}: "
                f"{self.MAX_ROUNDS} rounds x {self.ATTEMPTS_PER_ROUND} attempts",
            )

            total_attempts = self.MAX_ROUNDS * self.ATTEMPTS_PER_ROUND
            if attempts_completed:
                self._log_print(
                    "info",
                    f"Resuming group {group_suffix} after {attempts_completed}/"
                    f"{total_attempts} completed attempts",
                )
            for global_attempt in range(attempts_completed, total_attempts):
                round_index = global_attempt // self.ATTEMPTS_PER_ROUND + 1
                attempt_index = global_attempt % self.ATTEMPTS_PER_ROUND + 1
                try:
                    previous_code, previous_result, attempt_passed = self._run_attempt(
                        group_suffix=group_suffix,
                        round_index=round_index,
                        attempt_index=attempt_index,
                        previous_code=previous_code,
                        previous_result=previous_result,
                    )
                except Exception as exc:
                    previous_result = (
                        "The previous generation attempt failed before code execution. "
                        f"Return a valid submit_simulation_attempt call now. Error: {exc}"
                    )
                    self._log_print(
                        "error",
                        f"Round {round_index} attempt {attempt_index} failed: {exc}",
                    )
                    attempt_passed = False

                attempts_completed = global_attempt + 1
                group_context = self._load_json(self.sim_context_path)
                group_context["refinement_checkpoint"] = {
                    "attempts_completed": attempts_completed,
                    "previous_result": previous_result,
                    "validation_passed": attempt_passed,
                    "round": round_index,
                    "attempt": attempt_index,
                }
                self._save_json(self.sim_context_path, group_context)

                if attempt_passed:
                    validation_passed = True
                    passed_round = round_index
                    passed_attempt = attempt_index
                    self._log_print(
                        "info",
                        f"Validation passed at round {round_index}, attempt "
                        f"{attempt_index}; releasing group {group_suffix}",
                    )
                    break

            if not validation_passed:
                self._log_print(
                    "warn",
                    f"Group {group_suffix} did not pass validation after "
                    f"{attempts_completed} attempts",
                )

            result = {
                "group": group_suffix,
                "success": validation_passed,
                "score": None,
                "score_source": "not_evaluated",
                "validation_passed": validation_passed,
                "iterations": attempts_completed,
                "rounds": (attempts_completed + self.ATTEMPTS_PER_ROUND - 1)
                // self.ATTEMPTS_PER_ROUND,
                "attempts_per_round": self.ATTEMPTS_PER_ROUND,
                "passed_round": passed_round,
                "passed_attempt": passed_attempt,
                "agent": self.__class__.__name__,
            }
            context = self._load_json(self.sim_context_path)
            context["simulation_result"] = result
            self._save_json(self.sim_context_path, context)
            self.context_dict[f"simulation_result_{group_suffix}"] = result
            return {**result, "sim_context_path": self.sim_context_path}
        except Exception as exc:
            self._log_print("error", f"Refinement simulation failed: {exc}")
            traceback.print_exc()
            return {
                "success": False,
                "score": None,
                "score_source": "not_evaluated",
                "validation_passed": False,
                "iterations": attempts_completed,
                "group": group_suffix,
                "sim_context_path": self.sim_context_path,
                "error": str(exc),
                "agent": self.__class__.__name__,
            }
        finally:
            os.chdir(previous_directory)

    def run(self):
        """Process every group once; retries happen only inside each attempt."""
        self._log_print(
            "system",
            f"=== refinement run(): {len(self.task_table)} groups, "
            f"{self.MAX_ROUNDS} rounds x {self.ATTEMPTS_PER_ROUND} attempts ===",
        )
        for suffix in self.task_table:
            group_context_path = os.path.join(
                self.group_paths[suffix]["root"], "context.json"
            )
            saved_result = self._load_json(group_context_path).get(
                "simulation_result", {}
            )
            if not self.overwrite and saved_result.get("validation_passed") is True:
                self._log_print(
                    "info", f"Skipping group '{suffix}': validation already passed"
                )
                result = {
                    **saved_result,
                    "skipped": True,
                }
                self.context_dict[f"simulation_result_{suffix}"] = result
            else:
                result = self.single_modeling_run(suffix)
                self.context_dict[f"simulation_result_{suffix}"] = result
            if result.get("validation_passed"):
                self._publish_shared_artifacts(suffix, result)
            self._persist_global_context()

        self._generate_summary()
        self._persist_global_context()
        self._log_print("system", "All refinement simulation groups completed")

    def _publish_shared_artifacts(self, group_suffix, result):
        """Expose the one validated implementation at a stable shared path."""
        group_root = self.group_paths[group_suffix]["root"]
        shared_root = os.path.join(self.sim_root, self.SHARED_DIR_NAME)
        os.makedirs(shared_root, exist_ok=True)

        published = {}
        for name, relative_path in (
            ("solution", self.SOLUTION_PATH),
            ("validation", self.VALIDATION_PATH),
        ):
            source = os.path.join(group_root, relative_path)
            if os.path.isfile(source):
                destination = os.path.join(shared_root, os.path.basename(relative_path))
                shutil.copy2(source, destination)
                published[name] = os.path.relpath(destination, self.sim_root)

        source_results = os.path.join(group_root, "results")
        shared_results = os.path.join(shared_root, "results")
        if os.path.isdir(source_results):
            shutil.copytree(source_results, shared_results, dirs_exist_ok=True)
            published["results"] = os.path.relpath(shared_results, self.sim_root)

        manifest = {
            "source_group": group_suffix,
            "validation_passed": True,
            "published_at": self._utc(),
            "artifacts": published,
        }
        manifest_path = os.path.join(shared_root, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as file:
            json.dump(manifest, file, ensure_ascii=False, indent=2)
        manifest["manifest"] = os.path.relpath(manifest_path, self.sim_root)

        result["shared_artifacts"] = manifest
        self.context_dict["shared_simulation_artifacts"] = manifest
        self._log_print(
            "info", f"Published validated simulation artifacts to {shared_root}"
        )

    def _generate_summary(self):
        """Write a validation-based summary without inventing critic scores."""
        summary_path = os.path.join(self.sim_root, "summary.txt")
        results = [
            self.context_dict.get(f"simulation_result_{suffix}", {})
            for suffix in self.task_table
        ]
        with open(summary_path, "w", encoding="utf-8") as file:
            file.write(f"=== Refinement Simulation Summary ({self._utc()}) ===\n\n")
            file.write(f"Total groups: {len(results)}\n")
            file.write(
                "Validation passed: "
                f"{sum(1 for result in results if result.get('validation_passed'))}"
                f"/{len(results)}\n\n"
            )
            for result in results:
                status = "PASSED" if result.get("validation_passed") else "FAILED"
                file.write(f"Group {result.get('group', 'unknown')}: {status}\n")
                file.write(f"  Attempts completed: {result.get('iterations', 0)}\n")
                if result.get("passed_round") is not None:
                    file.write(
                        f"  Passed at: round {result['passed_round']}, "
                        f"attempt {result['passed_attempt']}\n"
                    )
                file.write("  Critic score: not evaluated\n\n")
        self._log_print("system", f"Summary report written to {summary_path}")
        return True
