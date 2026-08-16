"""Sequential query controllers used by the extraction pipeline."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Iterable, Mapping

from .admission import TopologyPlackettLuceAdmission, is_valid_arm


@dataclass
class AgeaBnrrAnchorController:
    """AGEA-style one-step anchor sampling over a BNRR-ranked candidate set.

    AGEA's candidate priority ``degree / (1 + pulls)`` is replaced by
    ``BNRR / (1 + pulls)``.  The final draw keeps AGEA's logarithmic degree
    weighting, mild query-count penalty, and recent-discovery boost.
    """

    candidate_k: int = 6
    seed: int = 42
    query_counts: dict[str, int] = field(default_factory=dict)
    rewards: dict[str, list[float]] = field(default_factory=dict)
    active_arms: tuple[str, ...] = ()
    epoch_id: int = 0
    admission_history: list[dict[str, object]] = field(default_factory=list)
    selection_history: list[dict[str, object]] = field(default_factory=list)
    _rng: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    @staticmethod
    def _max_queries(degree: int) -> int:
        if degree >= 100:
            return 10
        if degree >= 50:
            return 5
        if degree >= 20:
            return 3
        return 1

    def select(
        self,
        available: Iterable[str],
        turn: int,
        priors: Mapping[str, float] | None = None,
        *,
        degrees: Mapping[str, int] | None = None,
        recently_discovered: Iterable[str] = (),
    ) -> str | None:
        bnrr = priors or {}
        degrees = degrees or {}
        recent = set(str(arm) for arm in recently_discovered)
        eligible: list[dict[str, float | int | str]] = []
        for arm in sorted(set(str(item) for item in available)):
            raw_bnrr = max(0.0, float(bnrr.get(arm, 0.0)))
            if not is_valid_arm(arm) or raw_bnrr <= 0.0:
                continue
            degree = max(0, int(degrees.get(arm, 0)))
            pulls = max(0, int(self.query_counts.get(arm, 0)))
            max_queries = self._max_queries(degree)
            if pulls >= max_queries:
                continue
            eligible.append(
                {
                    "arm": arm,
                    "bnrr": raw_bnrr,
                    "degree": degree,
                    "pull_count": pulls,
                    "max_queries": max_queries,
                    "candidate_priority": raw_bnrr / (1.0 + pulls),
                }
            )

        eligible.sort(
            key=lambda item: (
                -float(item["candidate_priority"]),
                -float(item["bnrr"]),
                -int(item["degree"]),
                str(item["arm"]),
            )
        )
        candidates = eligible[: self.candidate_k]
        self.active_arms = tuple(str(item["arm"]) for item in candidates)
        self.epoch_id += 1

        weighted_candidates: list[dict[str, float | int | str | bool]] = []
        for item in candidates:
            arm = str(item["arm"])
            degree = int(item["degree"])
            pulls = int(item["pull_count"])
            recent_boost = 1.2 if arm in recent else 1.0
            weight = (
                max(math.log(degree + 1.0), 1.0)
                * recent_boost
                / (1.0 + pulls * 0.05)
            )
            weighted_candidates.append(
                {
                    **item,
                    "recently_discovered": arm in recent,
                    "sampling_weight": max(weight, 0.01),
                }
            )

        admission = {
            "policy": "agea_bnrr_topk",
            "epoch_id": self.epoch_id,
            "eligible_arm_count": len(eligible),
            "active_arms": list(self.active_arms),
            "candidates": weighted_candidates,
            "exploit_pull_start": turn,
            "exploit_pull_end": turn,
        }
        self.admission_history.append(admission)

        if not weighted_candidates:
            self.selection_history.append(
                {
                    "exploit_pull": turn,
                    "epoch_id": self.epoch_id,
                    "epoch_refreshed": True,
                    "selected_arm": None,
                    "reason": "no_bnrr_candidate",
                    "active_arms": [],
                }
            )
            return None

        total_weight = sum(
            float(item["sampling_weight"]) for item in weighted_candidates
        )
        uniform_draw = self._rng.random()
        threshold = uniform_draw * total_weight
        cumulative = 0.0
        chosen = weighted_candidates[-1]
        for item in weighted_candidates:
            cumulative += float(item["sampling_weight"])
            if threshold <= cumulative:
                chosen = item
                break

        selected = str(chosen["arm"])
        self.selection_history.append(
            {
                "exploit_pull": turn,
                "epoch_id": self.epoch_id,
                "epoch_refreshed": True,
                "selected_arm": selected,
                "reason": "agea_degree_weighted_random_from_bnrr_topk",
                "active_arms": list(self.active_arms),
                "uniform_draw": uniform_draw,
                "total_weight": total_weight,
                "conditional_probability": float(chosen["sampling_weight"])
                / total_weight,
            }
        )
        return selected

    def observe(self, arm: str | None, reward: float) -> None:
        if arm is None:
            return
        self.query_counts[arm] = self.query_counts.get(arm, 0) + 1
        self.rewards.setdefault(arm, []).append(float(reward))

    def state_dict(self) -> dict[str, object]:
        return {
            "policy": "agea_bnrr_anchor",
            "admission_policy": "bnrr_topk",
            "selection_policy": "agea_degree_weighted_random",
            "candidate_k": self.candidate_k,
            "seed": self.seed,
            "active_arms": list(self.active_arms),
            "epoch_id": self.epoch_id,
            "query_counts": self.query_counts,
            "rewards": self.rewards,
            "admission_history": self.admission_history,
            "selection_history": self.selection_history,
        }


@dataclass
class EpochFewaController:
    """A seeded, epoch-frozen FEWA-style rotting-bandit controller.

    Each entity is an arm and its observed reward is historical sensitive mass per
    candidate atom. TS-PL samples a set of arms that remains fixed for one exploit
    pull per admitted arm. The filtering pass uses recent windows of 1, 2, 4, ...
    pulls, which emphasizes decaying marginal yield.
    """

    delta: float = 0.05
    max_arms: int = 20
    seed: int = 42
    rewards: dict[str, list[float]] = field(default_factory=dict)
    active_arms: tuple[str, ...] = ()
    active_priors: dict[str, float] = field(default_factory=dict)
    epoch_end_turn: int = 0
    epoch_id: int = 0
    admission_history: list[dict[str, object]] = field(default_factory=list)
    selection_history: list[dict[str, object]] = field(default_factory=list)

    def _refresh_arms(
        self,
        available: Iterable[str],
        turn: int,
        priors: Mapping[str, float],
    ) -> bool:
        if self.active_arms and turn <= self.epoch_end_turn:
            return False

        self.epoch_id += 1
        available_arms = tuple(sorted(set(str(arm) for arm in available)))
        admission = TopologyPlackettLuceAdmission(seed=self.seed).admit(
            available_arms,
            priors,
            {arm: len(values) for arm, values in self.rewards.items()},
            max_arms=self.max_arms,
            epoch_id=self.epoch_id,
        )
        self.active_arms = admission.active_arms
        admission_record: dict[str, object] = admission.to_dict()
        # One exploit-pull opportunity per admitted arm defines the epoch.
        realized_epoch_length = max(1, len(self.active_arms))

        self.epoch_end_turn = turn + realized_epoch_length - 1
        self.active_priors = {
            arm: float(priors.get(arm, 0.0)) for arm in self.active_arms
        }
        for arm in self.active_arms:
            self.rewards.setdefault(arm, [])
        admission_record["exploit_pull_start"] = turn
        admission_record["exploit_pull_end"] = self.epoch_end_turn
        self.admission_history.append(admission_record)
        return True

    def select(
        self,
        available: Iterable[str],
        turn: int,
        priors: Mapping[str, float] | None = None,
    ) -> str | None:
        priors = priors or {}
        refreshed = self._refresh_arms(available, turn, priors)
        if not self.active_arms:
            self.selection_history.append(
                {
                    "exploit_pull": turn,
                    "epoch_id": self.epoch_id,
                    "epoch_refreshed": refreshed,
                    "selected_arm": None,
                    "reason": "no_active_arm",
                    "active_arms": [],
                }
            )
            return None

        # Topology is frozen with the admitted set. It is used only for
        # cold-start ordering and deterministic ties; FEWA's filtering signal
        # remains the attributable reward history.
        epoch_priors = self.active_priors

        unpulled = [arm for arm in self.active_arms if not self.rewards[arm]]
        if unpulled:
            selected = min(
                unpulled, key=lambda arm: (-epoch_priors.get(arm, 0.0), arm)
            )
            self.selection_history.append(
                {
                    "exploit_pull": turn,
                    "epoch_id": self.epoch_id,
                    "epoch_refreshed": refreshed,
                    "selected_arm": selected,
                    "reason": "globally_unpulled_topology_prior",
                    "active_arms": list(self.active_arms),
                    "unpulled_arms": list(unpulled),
                    "filter_windows": [],
                }
            )
            return selected

        active = list(self.active_arms)
        minimum_pulls = min(len(self.rewards[arm]) for arm in active)
        total_pulls = max(1, sum(len(values) for values in self.rewards.values()))
        window = 1
        filter_windows: list[dict[str, object]] = []
        while window <= minimum_pulls and len(active) > 1:
            means = {
                arm: sum(self.rewards[arm][-window:]) / window for arm in active
            }
            best_mean = max(means.values())
            confidence = math.sqrt(
                2.0
                * math.log(
                    max(2.0, 2.0 * total_pulls * len(active) / max(self.delta, 1e-12))
                )
                / window
            )
            retained = [
                arm for arm in active if means[arm] >= best_mean - 2.0 * confidence
            ]
            filter_windows.append(
                {
                    "window": window,
                    "means": means,
                    "best_mean": best_mean,
                    "confidence": confidence,
                    "input_arms": list(active),
                    "retained_arms": list(retained),
                }
            )
            active = retained
            window *= 2

        # FEWA balances pulls among statistically plausible arms.  Recent reward
        # and lexical order make ties reproducible.
        selected = min(
            active,
            key=lambda arm: (
                len(self.rewards[arm]),
                -self.rewards[arm][-1],
                -epoch_priors.get(arm, 0.0),
                arm,
            ),
        )
        self.selection_history.append(
            {
                "exploit_pull": turn,
                "epoch_id": self.epoch_id,
                "epoch_refreshed": refreshed,
                "selected_arm": selected,
                "reason": "fewa_filtered_least_pulled",
                "active_arms": list(self.active_arms),
                "retained_arms": list(active),
                "filter_windows": filter_windows,
            }
        )
        return selected

    def observe(self, arm: str | None, reward: float) -> None:
        if arm is None:
            return
        self.rewards.setdefault(arm, []).append(float(reward))

    def state_dict(self) -> dict[str, object]:
        return {
            "policy": "topology_pl_fewa",
            "epoch_length_semantics": "realized_active_set_size",
            "current_realized_epoch_length": len(self.active_arms),
            "delta": self.delta,
            "max_arms": self.max_arms,
            "admission_policy": "topology_plackett_luce",
            "seed": self.seed,
            "active_arms": list(self.active_arms),
            "active_priors": self.active_priors,
            "epoch_end_turn": self.epoch_end_turn,
            "epoch_id": self.epoch_id,
            "rewards": self.rewards,
            "admission_history": self.admission_history,
            "selection_history": self.selection_history,
        }


@dataclass(frozen=True)
class ModeDecision:
    """Auditable state for one explore/exploit decision."""

    mode: str
    reason: str
    epsilon: float
    effective_htsn_threshold: float
    recent_htsn: float | None
    recent_explore_success_rate: float | None
    explore_suppressed: bool
    available_arm_count: int

    def to_dict(self) -> dict[str, float | int | str | bool | None]:
        return {
            "mode": self.mode,
            "reason": self.reason,
            "epsilon": self.epsilon,
            "effective_htsn_threshold": self.effective_htsn_threshold,
            "recent_htsn": self.recent_htsn,
            "recent_explore_success_rate": self.recent_explore_success_rate,
            "explore_suppressed": self.explore_suppressed,
            "available_arm_count": self.available_arm_count,
        }


@dataclass
class AdaptiveModeController:
    """Use HTSN for mode choice without allowing an absorbing explore state.

    A fixed HTSN threshold can create an absorbing explore state when repeated
    broad queries keep the recent score at zero. This controller keeps HTSN as
    the decision signal while adding an adaptive threshold, an exploration-success
    guard, and a failed-explore streak cap.
    """

    initial_epsilon: float = 0.30
    epsilon_decay: float = 0.98
    min_epsilon: float = 0.05
    htsn_threshold: float = 0.15
    htsn_window: int = 5
    adaptive_threshold: bool = True
    explore_success_window: int = 20
    explore_success_min_samples: int = 5
    explore_success_threshold: float = 0.20
    max_consecutive_failed_explore: int = 2
    seed: int = 42
    _rng: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    def epsilon(self, turn: int) -> float:
        return max(
            self.min_epsilon,
            self.initial_epsilon * self.epsilon_decay ** max(0, turn - 1),
        )

    def choose(
        self,
        turn: int,
        available_arms: Iterable[str],
        htsn_history: list[float],
        mode_history: list[str] | None = None,
        meaningful_gain_history: list[bool] | None = None,
    ) -> ModeDecision:
        arms = list(available_arms)
        mode_history = mode_history or []
        meaningful_gain_history = meaningful_gain_history or []
        epsilon = self.epsilon(turn)
        threshold = self.htsn_threshold
        if self.adaptive_threshold and self.initial_epsilon > 0.0:
            threshold *= epsilon / self.initial_epsilon
        recent = htsn_history[-max(1, self.htsn_window) :]
        recent_htsn = sum(recent) / len(recent) if recent else None

        def decision(
            mode: str,
            reason: str,
            *,
            success_rate: float | None = None,
            explore_suppressed: bool = False,
        ) -> ModeDecision:
            return ModeDecision(
                mode=mode,
                reason=reason,
                epsilon=epsilon,
                effective_htsn_threshold=threshold,
                recent_htsn=recent_htsn,
                recent_explore_success_rate=success_rate,
                explore_suppressed=explore_suppressed,
                available_arm_count=len(arms),
            )

        if turn == 1:
            return decision("explore", "seed_turn")
        if not arms:
            return decision("explore", "no_anchor_available")

        recent_start = max(0, len(mode_history) - self.explore_success_window)
        recent_explore_gains = [
            bool(meaningful_gain_history[index])
            for index in range(
                recent_start,
                min(len(mode_history), len(meaningful_gain_history)),
            )
            if mode_history[index] == "explore"
        ]
        success_rate = None
        if len(recent_explore_gains) >= self.explore_success_min_samples:
            success_rate = sum(recent_explore_gains) / len(recent_explore_gains)
            if success_rate < self.explore_success_threshold:
                return decision(
                    "exploit",
                    f"low_explore_success({success_rate:.3f})",
                    success_rate=success_rate,
                    explore_suppressed=True,
                )

        # Productive broad queries are allowed to continue.  The cap is only a
        # rescue mechanism for consecutive explore turns with no new relation
        # and no positive history-anchored sensitive mass.
        consecutive_failed_explore = 0
        paired_history = zip(mode_history, meaningful_gain_history)
        for previous_mode, meaningful_gain in reversed(list(paired_history)):
            if previous_mode != "explore":
                break
            if meaningful_gain:
                break
            consecutive_failed_explore += 1
        if (
            self.max_consecutive_failed_explore > 0
            and consecutive_failed_explore
            >= self.max_consecutive_failed_explore
        ):
            return decision(
                "exploit",
                f"failed_explore_streak_cap({self.max_consecutive_failed_explore})",
                success_rate=success_rate,
                explore_suppressed=True,
            )

        if recent_htsn is not None and recent_htsn < threshold:
            return decision(
                "explore",
                f"recent_htsn_below_threshold({threshold:.4f})",
                success_rate=success_rate,
            )
        if self._rng.random() < epsilon:
            return decision(
                "explore",
                f"epsilon_sample({epsilon:.4f})",
                success_rate=success_rate,
            )
        return decision(
            "exploit",
            f"fewa({epsilon:.4f})",
            success_rate=success_rate,
        )


def rotting_diagnostics(
    rewards: Mapping[str, list[float]], tolerance: float = 1e-12
) -> dict[str, float | int | None]:
    """Measure observed violations of the FEWA non-increasing-yield assumption."""

    comparisons = 0
    increases = 0
    repeated_arms = 0
    for values in rewards.values():
        if len(values) < 2:
            continue
        repeated_arms += 1
        for previous, current in zip(values, values[1:]):
            comparisons += 1
            increases += int(current > previous + tolerance)
    return {
        "arms_with_repeated_queries": repeated_arms,
        "adjacent_reward_comparisons": comparisons,
        "reward_increases": increases,
        "violation_rate": increases / comparisons if comparisons else None,
    }
