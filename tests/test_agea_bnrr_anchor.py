import unittest

from extraction.control.controllers import AgeaBnrrAnchorController


class AgeaBnrrAnchorControllerTest(unittest.TestCase):
    def test_candidates_are_top_k_by_bnrr_underpull_priority(self) -> None:
        controller = AgeaBnrrAnchorController(candidate_k=2, seed=7)
        selected = controller.select(
            ["AA", "BB", "CC"],
            1,
            {"AA": 9.0, "BB": 8.0, "CC": 7.0},
            degrees={"AA": 30, "BB": 30, "CC": 30},
        )
        self.assertIn(selected, {"AA", "BB"})
        self.assertEqual(controller.active_arms, ("AA", "BB"))

        controller.observe("AA", 0.0)
        controller.observe("AA", 0.0)
        controller.select(
            ["AA", "BB", "CC"],
            2,
            {"AA": 9.0, "BB": 8.0, "CC": 7.0},
            degrees={"AA": 30, "BB": 30, "CC": 30},
        )
        self.assertEqual(controller.active_arms, ("BB", "CC"))

    def test_seeded_sampling_is_reproducible(self) -> None:
        args = (
            ["AA", "BB", "CC"],
            1,
            {"AA": 3.0, "BB": 2.0, "CC": 1.0},
        )
        kwargs = {"degrees": {"AA": 10, "BB": 5, "CC": 2}}
        left = AgeaBnrrAnchorController(candidate_k=3, seed=42)
        right = AgeaBnrrAnchorController(candidate_k=3, seed=42)
        self.assertEqual(left.select(*args, **kwargs), right.select(*args, **kwargs))


if __name__ == "__main__":
    unittest.main()
