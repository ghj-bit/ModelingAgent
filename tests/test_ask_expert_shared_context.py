import unittest
from unittest.mock import patch


class _Core:
    def __init__(self):
        self.calls = 0
        self.messages = []

    def execute(self, messages):
        self.calls += 1
        self.messages.append(messages)
        return "question" if self.calls % 2 else "answer"


class _Context:
    def __init__(self):
        self.context = {
            "modeling_question": "test question",
            "modeling_history_0_0": [{"model": "queueing model"}],
            "unrelated_future_output": "must not be exposed to AskExpert",
        }

    def add_context(self, key, value):
        self.context[key] = value


class AskExpertSharedContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from AFlow.workspace.ModelAgent.workflows.template import pipeline

        cls.pipeline = pipeline

    def test_refines_immediately_previous_stage_once(self):
        calls = []

        def refine_models(state):
            calls.append(state["rerun_advice"])
            state["rerun_advice"] = None
            state["last_stage"] = "RefineModels"
            return state

        state = {
            "core": _Core(),
            "shared_context": _Context(),
            "last_stage": "RefineModels",
            "complete": False,
        }
        with patch.dict(
            self.pipeline._STAGE_FUNCTIONS,
            {"RefineModels": refine_models},
        ):
            result = self.pipeline.ask_expert(state, rounds=2)

        self.assertIs(result, state)
        self.assertEqual(len(calls), 1)
        self.assertIn("Q1: question", calls[0])
        self.assertEqual(len(state["shared_context"].context["expert_advice"]), 2)
        self.assertTrue(
            all(
                item["target_stage"] == "RefineModels"
                for item in state["shared_context"].context["expert_advice"]
            )
        )
        self.assertEqual(
            state["shared_context"].context["expert_refinements"][-1]["rerun_count"],
            1,
        )
        first_prompt = str(state["core"].messages[0])
        self.assertIn("Immediately preceding stage: RefineModels", first_prompt)
        self.assertIn("modeling_history_0_0", first_prompt)
        self.assertNotIn("unrelated_future_output", first_prompt)
        self.assertNotIn("must not be exposed", first_prompt)
        expert_prompt = str(state["core"].messages[1])
        self.assertIn("LLM role-playing a domain expert", expert_prompt)
        self.assertIn("Stage being consulted about: RefineModels", expert_prompt)

    def test_rejects_simulate_and_later_stages_before_calling_llm(self):
        for stage in ("Simulate", "WriteData", "WriteSolution", "Review", None):
            with self.subTest(stage=stage):
                core = _Core()
                state = {
                    "core": core,
                    "shared_context": _Context(),
                    "last_stage": stage,
                    "complete": False,
                }
                with self.assertRaises(ValueError):
                    self.pipeline.ask_expert(state, rounds=1)
                self.assertEqual(core.calls, 0)

    def test_custom_expert_prompt_is_used_for_expert_role(self):
        def refine_models(state):
            state["rerun_advice"] = None
            state["last_stage"] = "RefineModels"
            return state

        state = {
            "core": _Core(),
            "shared_context": _Context(),
            "last_stage": "RefineModels",
            "complete": False,
        }
        with patch.dict(
            self.pipeline._STAGE_FUNCTIONS,
            {"RefineModels": refine_models},
        ):
            self.pipeline.ask_expert(
                state,
                rounds=1,
                expert_prompt="CUSTOM EXPERT ROLE PROMPT",
            )

        self.assertNotIn("CUSTOM EXPERT ROLE PROMPT", str(state["core"].messages[0]))
        self.assertIn("CUSTOM EXPERT ROLE PROMPT", str(state["core"].messages[1]))


if __name__ == "__main__":
    unittest.main()
