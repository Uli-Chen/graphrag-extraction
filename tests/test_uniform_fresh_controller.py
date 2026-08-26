import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from extraction.config import ExperimentConfig
from extraction.control.controllers import (
    EpochFewaController,
    FreshAnchorController,
)
from extraction.pipeline import MedicalExtractionPipeline


class FreshAnchorControllerTest(unittest.TestCase):
    def test_uses_every_positive_fresh_arm_before_repeating(self) -> None:
        controller = FreshAnchorController(seed=42)
        priors = {"ALPHA": 0.2, "BETA": 0.9, "GAMMA": 0.5}
        selected = []

        for turn in range(1, 4):
            arm = controller.select(priors, turn, priors)
            selected.append(arm)
            controller.observe(arm, 1.0)

        self.assertEqual(set(selected), set(priors))
        self.assertEqual(len(set(selected)), 3)
        self.assertEqual(
            [entry["reason"] for entry in controller.selection_history],
            ["uniform_fresh", "uniform_fresh", "uniform_fresh"],
        )

        repeated = controller.select(priors, 4, priors)
        self.assertIn(repeated, priors)
        self.assertEqual(
            controller.selection_history[-1]["reason"],
            "uniform_least_pulled",
        )

    def test_positive_bnrr_gate_and_arm_validation(self) -> None:
        controller = FreshAnchorController(seed=7)
        arms = ["ISOLATE", "SUMMARY", "CONNECTED"]
        priors = {"ISOLATE": 0.0, "SUMMARY": 0.8, "CONNECTED": 0.2}

        self.assertEqual(controller.select(arms, 1, priors), "CONNECTED")
        admission = controller.admission_history[-1]
        self.assertEqual(admission["eligible_arm_count"], 1)
        self.assertEqual(admission["eligibility_gate"], "bnrr_sensitivity>0")

    def test_seeded_selection_is_reproducible_and_reward_independent(self) -> None:
        priors = {f"ARM {index}": (index + 1) / 10 for index in range(10)}
        left = FreshAnchorController(seed=11)
        right = FreshAnchorController(seed=11)

        left_sequence = []
        right_sequence = []
        for turn in range(1, 11):
            left_arm = left.select(priors, turn, priors)
            right_arm = right.select(priors, turn, priors)
            left_sequence.append(left_arm)
            right_sequence.append(right_arm)
            left.observe(left_arm, 0.0)
            right.observe(right_arm, 1.0)

        self.assertEqual(left_sequence, right_sequence)
        self.assertFalse(left.state_dict()["reward_used_for_selection"])


class UniformFreshConfigurationTest(unittest.TestCase):
    def test_uniform_fresh_is_the_default_policy(self) -> None:
        self.assertEqual(
            ExperimentConfig().anchor_sampling_policy,
            "uniform_fresh",
        )

    def test_pipeline_routes_default_and_legacy_policies(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)

            def build(policy: str, run_id: str) -> MedicalExtractionPipeline:
                config = ExperimentConfig(
                    graph_root=str(root),
                    data_dir=str(root),
                    output_root=str(root / "runs"),
                    run_id=run_id,
                    anchor_sampling_policy=policy,
                )
                with (
                    patch("extraction.pipeline.TruthData.load", return_value=Mock()),
                    patch(
                        "extraction.pipeline.AgeaGraphRagAdapter",
                        return_value=Mock(),
                    ),
                ):
                    return MedicalExtractionPipeline(config)

            default_pipeline = build("uniform_fresh", "default")
            legacy_pipeline = build("ts_pl_fewa", "legacy")

            self.assertIsInstance(
                default_pipeline.arm_controller,
                FreshAnchorController,
            )
            self.assertIsInstance(
                legacy_pipeline.arm_controller,
                EpochFewaController,
            )


if __name__ == "__main__":
    unittest.main()
