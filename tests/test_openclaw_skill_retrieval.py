import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

from src.OpenClaw import baseline
from src.OpenClaw import run_modelingbench_skill_retrieval as retrieval


class SkillRetrievalTests(unittest.TestCase):
    def test_skill_retrieval_keeps_its_own_skill_prompt(self):
        prompt = retrieval.SKILL_RETRIEVAL_PROMPT_TEMPLATE_PATH.read_text(
            encoding="utf-8"
        )
        self.assertIn("Workspace skills", prompt)
        self.assertIn("SKILL.md", prompt)

    def test_catalog_and_retrieval_select_only_top_relevant_skills(self):
        catalog = retrieval.load_skill_catalog(baseline.SCRIPT_DIR / "skills")
        result = retrieval.retrieve_skills(
            {
                "title": "Finite-horizon queue simulation",
                "question": (
                    "Compare steady-state queueing formulas with a transient "
                    "simulation and reconcile different waiting-time estimates."
                ),
            },
            catalog,
            top_k=2,
            relative_threshold=0.0,
        )
        self.assertLessEqual(len(result["selected_skills"]), 2)
        self.assertIn("reconcile-static-dynamic-models", result["selected_skills"])
        self.assertEqual(len(result["ranking"]), len(catalog))

    def test_default_catalog_excludes_patch_fusion_skill(self):
        catalog = retrieval.load_skill_catalog(
            baseline.SCRIPT_DIR / "skills",
            retrieval.DEFAULT_EXCLUDED_SKILLS,
        )
        self.assertNotIn(
            "fuse-verified-patches",
            {item["directory"] for item in catalog},
        )

    def test_retrieval_query_does_not_include_judge_information(self):
        query = retrieval.problem_query(
            {
                "title": "Task",
                "question": "Original question",
                "decomposition": {"grading_points": ["SECRET_GRADING_POINT"]},
                "eval_roles": ["SECRET_ROLE"],
            }
        )
        self.assertNotIn("SECRET", query)

    def test_only_declared_skill_sections_are_indexed(self):
        with tempfile.TemporaryDirectory() as temporary:
            skill_dir = Path(temporary) / "section-test"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\n"
                "name: section-test\n"
                "description: visible description\n"
                "---\n\n"
                "## Workflow\nHIDDEN_WORKFLOW_TOKEN\n\n"
                "## Generalization Examples\nVISIBLE_EXAMPLE_TOKEN\n\n"
                "## Notes\nHIDDEN_NOTES_TOKEN\n",
                encoding="utf-8",
            )
            skill = retrieval.parse_skill(skill_dir)
            tokens = set(skill["tokens"])
            self.assertIn("visible_example_token", tokens)
            self.assertNotIn("hidden_workflow_token", tokens)
            self.assertNotIn("hidden_notes_token", tokens)

    def test_prepare_run_copies_only_selected_skills(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "skills"
            for name in ("first-skill", "second-skill"):
                folder = source / name
                folder.mkdir(parents=True)
                (folder / "SKILL.md").write_text(
                    f"---\nname: {name}\ndescription: test\n---\n",
                    encoding="utf-8",
                )
            run_dir, output_dir, _ = baseline.prepare_run(
                "example",
                {
                    "title": "Example",
                    "source": "Test",
                    "year": 2026,
                    "question": "Build a model.",
                },
                root / "runs",
                "test-model",
                skills_source=source,
                selected_skills=["second-skill"],
            )
            self.assertFalse((output_dir / "skills/first-skill").exists())
            self.assertTrue((output_dir / "skills/second-skill/SKILL.md").is_file())
            metadata = (run_dir / "meta/run.json").read_text(encoding="utf-8")
            self.assertNotIn('"first-skill"', metadata)
            self.assertIn('"second-skill"', metadata)

    def test_repeated_judge_result_record_uses_average_scores(self):
        dimensions = {name: 0.6 for name in baseline.EXPECTED_JUDGERS}
        record = retrieval.result_record(
            "example",
            {
                "run_dir": Path("run"),
                "final_report": Path("run/report.md"),
                "judge_result": Path("run/raw.json"),
                "repeated_judge": True,
                "judge_stability_result": Path("run/judge_stability.json"),
                "judge_repeats": 3,
                "average_score": 0.6,
                "dimension_scores": dimensions,
            },
            {"selected_skills": ["example-skill"]},
        )
        self.assertEqual(record["judge_repeats"], 3)
        self.assertEqual(record["average_score"], 0.6)
        self.assertEqual(record["dimension_scores"], dimensions)
        self.assertEqual(record["judge_result"], str(Path("run/raw.json")))
        json.dumps(record)

    def test_load_existing_run_reuses_report_and_validates_skills(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run_dir = root / "test-model" / "example_20260904_093438"
            report = run_dir / "output" / "results" / "solution_report.md"
            report.parent.mkdir(parents=True)
            report.write_text("finished report", encoding="utf-8")
            metadata = run_dir / "meta" / "run.json"
            metadata.parent.mkdir()
            metadata.write_text(
                json.dumps(
                    {
                        "problem_id": "example",
                        "model": "test/model",
                        "final_report": str(report),
                        "installed_skills": ["example-skill"],
                    }
                ),
                encoding="utf-8",
            )
            result = retrieval.load_existing_run(
                "example",
                Namespace(
                    output_root=str(root),
                    model="test/model",
                    resume_run_timestamp="20260904_093438",
                ),
                {"selected_skills": ["example-skill"]},
            )
            self.assertEqual(result["run_dir"], run_dir)
            self.assertEqual(result["final_report"], report)


if __name__ == "__main__":
    unittest.main()
