import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.OpenClaw import baseline
from src.OpenClaw import run_judge_stability


class JudgeStabilityTests(unittest.TestCase):
    def test_parse_direct_report_specs(self):
        with tempfile.TemporaryDirectory() as temporary:
            report = Path(temporary) / "solution_report.md"
            report.write_text("# Report", encoding="utf-8")
            parsed = run_judge_stability.parse_report_specs(
                [f"baseline={report}"]
            )
            self.assertEqual(parsed, {"baseline": report.resolve()})

    def test_parse_direct_report_specs_rejects_invalid_label(self):
        with self.assertRaises(ValueError):
            run_judge_stability.parse_report_specs(["missing-separator"])

    def test_repeated_evaluation_reuses_existing_judge_aggregation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            report = root / "solution_report.md"
            report.write_text("# Report", encoding="utf-8")
            raw_result = root / "raw_judge.json"
            raw_result.write_text(
                __import__("json").dumps(
                    {
                        "judgements": {
                            name: {"calculated_overall": 0.5}
                            for name in baseline.EXPECTED_JUDGERS
                        }
                    }
                ),
                encoding="utf-8",
            )
            with patch.object(
                run_judge_stability.openclaw_baseline,
                "judge_final_report",
                return_value=raw_result,
            ):
                payload = run_judge_stability.evaluate_reports_repeated(
                    "example",
                    {"report": report},
                    2,
                    "test-judge",
                    root / "judge_stability.json",
                    root,
                )
            average = payload["average_scores"]["round_report"]
            self.assertEqual(average["trial_count"], 2)
            self.assertEqual(average["average_overall_score"], 0.5)
            self.assertTrue((root / "judge_stability.json").is_file())

    def test_selected_judgers_are_forwarded_and_only_they_are_scored(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            report = root / "solution_report.md"
            report.write_text("# Report", encoding="utf-8")
            raw_result = root / "raw_judge.json"
            raw_result.write_text(
                __import__("json").dumps(
                    {
                        "judgements": {
                            name: {"calculated_overall": 0.5}
                            for name in baseline.EXPECTED_JUDGERS
                        }
                    }
                ),
                encoding="utf-8",
            )
            selected = (
                "structural_coherency",
                "scoring_decomposition",
                "modeling_groundedness",
                "analysis_groundedness",
            )
            with patch.object(
                run_judge_stability.openclaw_baseline,
                "judge_final_report",
                return_value=raw_result,
            ) as judge:
                payload = run_judge_stability.evaluate_reports_repeated(
                    "example",
                    {"report": report},
                    1,
                    "test-judge",
                    root / "judge_stability.json",
                    root,
                    judgers=selected,
                )

            self.assertEqual(judge.call_args.kwargs["judgers"], selected)
            scores = payload["evaluations"]["report"][0]["dimension_scores"]
            self.assertEqual(tuple(scores), selected)


if __name__ == "__main__":
    unittest.main()
