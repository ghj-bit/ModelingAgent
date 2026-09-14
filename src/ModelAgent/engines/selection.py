import json
from copy import deepcopy

from src.ModelAgent.engines.core import Core

from src.ModelAgent.prompts.assumption import ASSUMPPTION_SYS, ASSUMPPTION_USER
from src.ModelAgent.prompts.question_extract import EXTRACT_MODELING_SYS, EXTRACT_MODELING_USER
from src.ModelAgent.prompts.selection_critic import SELECT_CRITIC_SYS, SELECT_CRITIC_USER
from src.ModelAgent.prompts.selection_generate import SELECT_GEN_SYS, SELECT_GEN_USER, SELECT_GEN_REFINE

from src.ModelAgent.utils.utils import execute_json, form_message
from src.ModelAgent.utils.shared_context import SharedContext

class SelectionEngine:
    def __init__(self, config, core, shared_context):
        self.config = config
        self.query = config["query"]
        self.core: Core = core
        self.shared_context: SharedContext = shared_context

    @staticmethod
    def _collapse_to_single_task(proposed_model):
        """Turn an accidental decomposition into one end-to-end modeling task."""
        tasks = proposed_model.get("task_decomposition", [])
        if len(tasks) <= 1:
            return proposed_model

        objectives = [task.get("objective", "").strip() for task in tasks]
        analyses = [task.get("analysis", "").strip() for task in tasks]
        method_names = []
        for task in tasks:
            approaches = task.get("modeling_approaches") or []
            if approaches and approaches[0].get("approach"):
                method_names.append(approaches[0]["approach"].strip())

        proposed_model["task_decomposition"] = [
            {
                "subtask": "Solve the complete modeling problem with one shared workflow",
                "objective": " ".join(filter(None, objectives)),
                "analysis": "\n\n".join(filter(None, analyses)),
                "modeling_approaches": [
                    {
                        "approach": "Unified end-to-end modeling and simulation",
                        "application": (
                            "Build one reusable computational model that addresses every "
                            "requirement in sequence. Generate and validate one shared "
                            "implementation, reuse its quantitative artifacts for scenario "
                            "analysis and decisions, and leave report composition to the "
                            "writing stage. Candidate techniques from the proposal: "
                            + ", ".join(method_names)
                            + "."
                        ),
                    }
                ],
            }
        ]
        return proposed_model

    def get_modeling_question(self, advice=None):
        print("Getting modeling question")
        system = EXTRACT_MODELING_SYS
        user = EXTRACT_MODELING_USER.format(original_text=self.query)
        if advice:
            user += "\n\n## Expert Advice (must be incorporated)\n" + advice
        messages = form_message(system, user)
        response = self.core.execute(messages)
        self.modeling_question = response.strip()
        print(">> Modeling question:\n", self.modeling_question)
        self.shared_context.add_context("modeling_question", self.modeling_question)
        
    
    def get_assumptions(self, advice=None):
        print("Getting assumptions")
        system = ASSUMPPTION_SYS
        user = ASSUMPPTION_USER.format(modeling_question=self.modeling_question)
        if advice:
            user += "\n\n## Expert Advice (must be incorporated)\n" + advice
        messages = form_message(system, user)
        self.assumptions, response = execute_json(self.core, messages)
        print(">> Assumptions:\n", response)
        self.shared_context.add_context("assumptions", self.assumptions)
    
    
    def selection_refine_loop(self, advice=None):
        history = []

        system = SELECT_GEN_SYS
        user = SELECT_GEN_USER.format(modeling_question=self.modeling_question)
        if self.config.get("single_task_mode"):
            user += (
                "\n\n## Single-task mode (mandatory)\n"
                "Return exactly one item in task_decomposition. That item must cover the "
                "complete problem with one shared computational model. Treat input "
                "preparation, scenario evaluation, decision analysis, and communication "
                "as stages of that one task, not independent subtasks. The implementation "
                "must be generated and validated only once and reused by later stages."
            )
        if advice:
            user += "\n\n## Expert Advice (must be incorporated)\n" + advice
        
        round = 0
        while round < self.config["selection"]["rounds"]:
            round += 1
            print(f"Model proposing round {round}...")
            
            messages = form_message(system, user)
            proposed_model, _ = execute_json(self.core, messages)
            if self.config.get("single_task_mode"):
                proposed_model = self._collapse_to_single_task(proposed_model)
            print(">> Proposed model:\n", json.dumps(proposed_model, ensure_ascii=False, indent=2))

            # history.append(deepcopy(proposed_model))
            subtasks = proposed_model["task_decomposition"]
            
            all_critics = []
            for subtask in subtasks:
                system = SELECT_CRITIC_SYS
                user = SELECT_CRITIC_USER.format(subtask=subtask)
                messages = form_message(system, user)
                # from IPython import embed; embed()
                critics, _ = execute_json(self.core, messages)
                print(">> Critics:\n", json.dumps(critics, ensure_ascii=False, indent=2))

                all_critics.extend(deepcopy(critics))
                
                for critic in critics:
                    approach = critic.pop("approach")
                    for modeling_approach in subtask["modeling_approaches"]:
                        if modeling_approach["approach"] == approach:
                            # the variable propose_model is updated in place, now with user feedback
                            modeling_approach["user_feedback"] = critic
                            break
                            
            # history.append(deepcopy(all_critics))
            history.append(deepcopy(proposed_model))
            
            system = SELECT_GEN_SYS
            user = SELECT_GEN_REFINE.format(modeling_question=self.modeling_question, proposed_model=proposed_model)
            if self.config.get("single_task_mode"):
                user += (
                    "\n\n## Single-task mode (mandatory)\n"
                    "Keep exactly one item in task_decomposition and one shared "
                    "end-to-end implementation. Do not split reporting, validation, "
                    "scenario analysis, or data preparation into separate tasks."
                )
        
        self.shared_context.add_context("selection_history", history)
        self.proposed_model = proposed_model
        # May further add some selection / ranking techniques to select the best model
        self.rank_proposed_model()
        # Later may only adopt the top-k models for trial
        
        
    def rank_proposed_model(self):
        # In-place sorting of the modeling_approaches based on the user_feedback["overall_score"]
        for subtask in self.proposed_model["task_decomposition"]:
            # sort the modeling_approach based on the modeling_approach["user_feedback"]["overall_score"]
            subtask["modeling_approaches"] = sorted(subtask["modeling_approaches"], key=lambda x: x["user_feedback"]["overall_score"], reverse=True)
        
        
        
        
            
        
            
        
