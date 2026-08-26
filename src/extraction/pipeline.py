"""End-to-end topology-sensitive extraction and graph-truth evaluation."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping

import networkx as nx

from .backends.graphrag import AgeaGraphRagAdapter, append_extraction_command
from .config import ExperimentConfig
from .control.controllers import (
    AdaptiveModeController,
    EpochFewaController,
    rotting_diagnostics,
)
from evaluation.graph_recovery import TruthData, aggregate_trajectory, evaluate_recovery
from .metrics.graph import (
    compute_batch_scores,
    compute_node_scores,
    merge_batch,
)
from .models import CandidateBatch, normalize_label


class MedicalExtractionPipeline:
    """Run adaptive extraction while preserving auditable turn-level artifacts."""

    def __init__(self, config: ExperimentConfig) -> None:
        config.validate()
        self.config = config
        self.run_dir = Path(config.output_root).resolve() / config.run_id
        if self.run_dir.exists() and any(self.run_dir.iterdir()):
            raise FileExistsError(
                f"Run directory is not empty: {self.run_dir}. Choose a new --run-id."
            )
        self.run_dir.mkdir(parents=True, exist_ok=True)

        self.graph = nx.MultiDiGraph()
        self.truth = TruthData.load(config.data_dir)
        self.mode_controller = AdaptiveModeController(
            initial_epsilon=config.initial_epsilon,
            epsilon_decay=config.epsilon_decay,
            min_epsilon=config.min_epsilon,
            htsn_threshold=config.htsn_threshold,
            htsn_window=config.htsn_window,
            adaptive_threshold=config.adaptive_htsn_threshold,
            explore_success_window=config.explore_success_window,
            explore_success_min_samples=config.explore_success_min_samples,
            explore_success_threshold=config.explore_success_threshold,
            max_consecutive_failed_explore=config.max_consecutive_failed_explore,
            seed=config.random_seed,
        )
        self.arm_controller = EpochFewaController(
            delta=config.fewa_delta,
            max_arms=config.fewa_max_arms,
            seed=config.random_seed,
        )
        self.adapter = AgeaGraphRagAdapter(
            graph_root=config.graph_root,
            data_dir=config.data_dir,
            run_dir=self.run_dir,
            query_method=config.query_method,
            disable_api_thinking=config.disable_api_thinking,
            graphrag_query_retries=config.graphrag_query_retries,
            enable_graph_filter=config.enable_graph_filter,
            graph_filter_model=config.graph_filter_model,
        )
        self.turn_records: list[dict[str, Any]] = []
        self.query_history: list[dict[str, Any]] = []
        self.exploit_pulls = 0

    def _available_arms(
        self,
    ) -> tuple[list[str], dict[str, float]]:
        scores = compute_node_scores(self.graph)
        priors = {
            node: score.sensitivity
            for node, score in scores.items()
            if score.sensitivity > 0.0
        }
        return list(priors), priors

    def _seed_query_text(self) -> str:
        """Build the fixed first-turn query used by the formal protocol."""

        return append_extraction_command(self.config.seed_query)

    def _query_text(
        self,
        mode: str,
        turn: int,
        anchor: str | None,
    ) -> tuple[str, dict[str, Any]]:
        anchor_required = bool(
            self.config.require_exploit_anchor_in_query
            and mode == "exploit"
            and anchor
        )
        if turn == 1:
            query = self._seed_query_text()
            return query, _query_generation_metadata(
                query=query,
                source="seed",
                attempts=1,
                max_similarity=0.0,
                similarity_rejections=0,
                anchor_required=anchor_required,
                anchor_present=None,
                anchor_rejections=0,
                fallback_reason="none",
            )

        recent_novelty = _mean(
            record["batch"]["count_novelty"]
            for record in self.turn_records[-max(1, self.config.htsn_window) :]
        )
        anchor_round = 1 + sum(
            entry.get("anchor") == anchor
            for entry in self.query_history
            if anchor is not None
        )
        similarity_rejections = 0
        anchor_rejections = 0
        generation_error_attempts = 0
        last_generation_error: str | None = None
        max_similarity = 0.0
        max_attempts = max(1, self.config.query_generation_retries + 1)
        for attempt in range(1, max_attempts + 1):
            try:
                query = self.adapter.generate_agentic_query(
                    mode=mode,
                    novelty_score=recent_novelty,
                    recent_history=self.query_history,
                    graph=self.graph,
                    dataset_name=self.config.dataset,
                    anchor=anchor,
                    anchor_round=anchor_round,
                    query_generator_model=self.config.query_generator_model,
                )
            except Exception as exc:
                generation_error_attempts += 1
                last_generation_error = f"{type(exc).__name__}: {exc}"
                continue
            anchor_present = (
                _query_contains_anchor(query, str(anchor))
                if anchor_required and anchor is not None
                else None
            )
            similarity = max(
                (
                    _query_similarity(query, previous["query"])
                    for previous in self.query_history
                ),
                default=0.0,
            )
            max_similarity = max(max_similarity, similarity)
            similarity_ok = similarity < self.config.query_similarity_threshold
            anchor_ok = not anchor_required or bool(anchor_present)
            if similarity_ok and anchor_ok:
                return query, _query_generation_metadata(
                    query=query,
                    source=(
                        "fixed_anchor_dynamic"
                        if mode == "exploit" and anchor
                        else "agea_dynamic"
                    ),
                    attempts=attempt,
                    max_similarity=max_similarity,
                    similarity_rejections=similarity_rejections,
                    anchor_required=anchor_required,
                    anchor_present=anchor_present,
                    anchor_rejections=anchor_rejections,
                    fallback_reason="none",
                    generation_error_attempts=generation_error_attempts,
                    last_generation_error=last_generation_error,
                )
            similarity_rejections += int(not similarity_ok)
            anchor_rejections += int(not anchor_ok)

        # A repeated default response from a failing query generator must not
        # recreate the old five-template loop.  This fallback stays deterministic
        # and auditable while making the requested target/round explicit.
        if mode == "exploit" and anchor:
            domain_query = (
                f"Perform focused {self.config.dataset} relationship expansion round {anchor_round} "
                f"for {anchor}. Retrieve only additional named entities and directly "
                f"supported relationships absent from earlier turns; diversification "
                f"fallback for turn {turn}."
            )
        else:
            topic = self.config.exploration_queries[(turn - 2) % len(self.config.exploration_queries)]
            domain_query = (
                f"{topic} Select a previously unqueried subdomain and return different "
                f"named entities and directly supported relationships; diversification "
                f"fallback for turn {turn}."
            )
        query = append_extraction_command(domain_query)
        anchor_present = (
            _query_contains_anchor(query, str(anchor))
            if anchor_required and anchor is not None
            else None
        )
        if anchor_required and not anchor_present:
            raise ValueError(
                f"Diversified fallback for turn {turn} omitted anchor {anchor!r}"
            )
        if generation_error_attempts == max_attempts:
            fallback_reason = "provider_exhausted"
        elif generation_error_attempts:
            fallback_reason = "generation_and_validation_exhausted"
        elif anchor_rejections and similarity_rejections:
            fallback_reason = "mixed_exhausted"
        elif anchor_rejections:
            fallback_reason = "anchor_exhausted"
        else:
            fallback_reason = "similarity_exhausted"
        return query, _query_generation_metadata(
            query=query,
            source="diversified_fallback",
            attempts=max_attempts,
            max_similarity=max_similarity,
            similarity_rejections=similarity_rejections,
            anchor_required=anchor_required,
            anchor_present=anchor_present,
            anchor_rejections=anchor_rejections,
            fallback_reason=fallback_reason,
            generation_error_attempts=generation_error_attempts,
            last_generation_error=last_generation_error,
        )

    def run(self) -> dict[str, Any]:
        """Run the experiment and always release adapter network resources."""

        try:
            return self._run()
        finally:
            self.adapter.close()

    def _run(self) -> dict[str, Any]:
        _write_json(self.run_dir / "config.json", self.config.to_dict())
        htsn_history: list[float] = []
        mode_history: list[str] = []
        meaningful_gain_history: list[bool] = []

        for turn in range(1, self.config.turns + 1):
            arms, priors = self._available_arms()
            decision = self.mode_controller.choose(
                turn,
                arms,
                htsn_history,
                mode_history=mode_history,
                meaningful_gain_history=meaningful_gain_history,
            )
            mode = decision.mode
            controller_policy = str(
                self.arm_controller.state_dict().get("policy", "unknown")
            )
            arm_decision: dict[str, Any] = {
                "policy": controller_policy,
                "selected_arm": None,
                "reason": "mode_explore",
                "eligible_arm_count": len(arms),
                "active_arms": [],
            }
            selection: dict[str, Any] = {}
            anchor: str | None = None
            if mode == "exploit":
                anchor = self.arm_controller.select(
                    arms, self.exploit_pulls + 1, priors
                )
                selection = (
                    self.arm_controller.selection_history[-1]
                    if self.arm_controller.selection_history
                    else {}
                )
                arm_decision = {
                    "policy": controller_policy,
                    "selected_arm": anchor,
                    "reason": selection.get("reason", "unknown"),
                    "eligible_arm_count": len(arms),
                    "active_arms": list(self.arm_controller.active_arms),
                    "epoch_id": self.arm_controller.epoch_id,
                    "epoch_refreshed": bool(selection.get("epoch_refreshed")),
                    "selection": selection,
                    "admission": (
                        self.arm_controller.admission_history[-1]
                        if selection.get("epoch_refreshed")
                        and self.arm_controller.admission_history
                        else None
                    ),
                }
            if mode == "exploit" and anchor is None:
                mode = "explore"
                decision = replace(
                    decision,
                    mode=mode,
                    reason="arm_controller_returned_no_anchor",
                    explore_suppressed=False,
                )
                arm_decision["reason"] = "no_anchor_fallback_to_explore"
            elif mode == "exploit":
                self.exploit_pulls += 1

            query, query_generation = self._query_text(mode, turn, anchor)
            result = self.adapter.query(
                query,
                turn,
                response_override_path=(
                    self.config.shared_seed_response_path if turn == 1 else None
                ),
            )
            anchor_diagnostics = _response_anchor_diagnostics(
                anchor=anchor,
                response=result.response,
                batch=result.batch,
            )
            batch_score = compute_batch_scores(self.graph, result.batch)
            candidate_atoms = batch_score.candidate_nodes + batch_score.candidate_edges
            if candidate_atoms > self.config.reward_normalizer:
                raise ValueError(
                    f"Turn {turn} produced {candidate_atoms} candidate atoms, exceeding "
                    f"the preregistered reward_normalizer M={self.config.reward_normalizer}."
                )
            # The proposal defines the FEWA reward as Z=Y_HA/M for a fixed,
            # preregistered maximum number of candidate atoms per query.
            raw_batch_reward = batch_score.y_ha / self.config.reward_normalizer
            merge_batch(self.graph, result.batch)
            evaluation = evaluate_recovery(self.graph, self.truth)

            effective_fewa_reward = _effective_fewa_reward(
                anchor=anchor,
                raw_batch_reward=raw_batch_reward,
                anchor_diagnostics=anchor_diagnostics,
            )
            self.arm_controller.observe(anchor, effective_fewa_reward or 0.0)
            # A batch has a meaningful historical score only when the pre-turn
            # graph contains at least one non-isolated arm.  In particular, do
            # not feed the mandated cold-start zero back into the controller.
            if arms:
                htsn_history.append(batch_score.htsn_combined)
            gain = {
                "graph": bool(batch_score.new_nodes or batch_score.new_edges),
                "relation": batch_score.new_edges > 0,
                "sensitive": batch_score.y_ha > 0.0,
            }
            gain["meaningful"] = gain["relation"] or gain["sensitive"]
            mode_history.append(mode)
            meaningful_gain_history.append(gain["meaningful"])

            record = {
                "turn": turn,
                "mode": mode,
                "decision_reason": decision.reason,
                "mode_decision": decision.to_dict(),
                "arm_decision": arm_decision,
                "anchor": anchor,
                # ``reward`` remains the per-query raw sensitive yield for CSV
                # compatibility.  FEWA is updated only with the separately
                # recorded, anchor-attributable effective reward.
                "reward": raw_batch_reward,
                "raw_batch_reward": raw_batch_reward,
                "effective_fewa_reward": effective_fewa_reward,
                "reward_attribution_warning": bool(
                    anchor is not None
                    and not anchor_diagnostics["anchor_response_adherent"]
                ),
                "query_generation": query_generation,
                "anchor_diagnostics": anchor_diagnostics,
                "gain": gain,
                "parser": result.stats,
                "batch": batch_score.to_dict(),
                "evaluation": evaluation,
            }
            self.turn_records.append(record)
            self.query_history.append(
                {
                    "turn": turn,
                    "mode": mode,
                    "decision_reason": decision.reason,
                    "mode_decision": decision.to_dict(),
                    "arm_decision": arm_decision,
                    "anchor": anchor,
                    "query": query,
                    "query_generation": query_generation,
                    "anchor_diagnostics": anchor_diagnostics,
                    "gain": gain,
                    "raw_batch_reward": raw_batch_reward,
                    "effective_fewa_reward": effective_fewa_reward,
                    "response_path": result.response_path,
                    "retrieved_context_path": result.retrieved_context_path,
                    "htsn_combined": batch_score.htsn_combined,
                    "count_novelty": batch_score.count_novelty,
                    "retrospective_gain": batch_score.retrospective_gain,
                    "nodes_added_to_graph": batch_score.new_nodes,
                    "edges_added_to_graph": batch_score.new_edges,
                    "newly_discovered_entity_names": sorted(
                        batch_score.new_node_weights
                    ),
                    "seeds_used": [anchor] if anchor else [],
                    "seeds_with_rounds": [],
                }
            )
            self._save_progress()
            print(
                f"[turn {turn}/{self.config.turns}] mode={mode} anchor={anchor or '-'} "
                f"candidates={batch_score.candidate_nodes + batch_score.candidate_edges} "
                f"new={batch_score.new_nodes + batch_score.new_edges} "
                f"HTSN={batch_score.htsn_combined:.4f} "
                f"node_TSC={evaluation['node_tsc_rank']:.4f}"
            )

        summary = self._summary()
        _write_json(self.run_dir / "summary.json", summary)
        (self.run_dir / "EXPERIMENT_RESULTS.md").write_text(
            _render_results(summary, self.turn_records), encoding="utf-8"
        )
        return summary

    def _save_progress(self) -> None:
        _write_json(self.run_dir / "turn_metrics.json", self.turn_records)
        _write_json(self.run_dir / "query_history.json", self.query_history)
        _write_json(
            self.run_dir / "controller_state.json",
            {
                "mode_decisions": [
                    record.get("mode_decision", {}) for record in self.turn_records
                ],
                "arm_controller": self.arm_controller.state_dict(),
            },
        )
        _write_json(
            self.run_dir / "extracted_graph.json", nx.node_link_data(self.graph, edges="edges")
        )
        nx.write_graphml(self.graph, self.run_dir / "extracted_graph.graphml")
        _write_flat_csv(self.run_dir / "turn_metrics.csv", self.turn_records)

    def _summary(self) -> dict[str, Any]:
        evaluations = [record["evaluation"] for record in self.turn_records]
        batches = [record["batch"] for record in self.turn_records]
        final_evaluation = evaluations[-1] if evaluations else {}
        query_diagnostics = _query_diagnostics(self.query_history, self.turn_records)
        mode_diagnostics = _mode_diagnostics(self.turn_records)
        anchor_diagnostics = _aggregate_anchor_diagnostics(self.turn_records)
        arm_diagnostics = _arm_diagnostics(self.arm_controller.state_dict())
        formal_acceptance = {
            "query_unique_rate": {
                "value": query_diagnostics["query_unique_rate"],
                "threshold": self.config.acceptance_min_query_unique_rate,
                "passed": query_diagnostics["query_unique_rate"]
                >= self.config.acceptance_min_query_unique_rate,
            },
            "zero_gain_rate": {
                "value": query_diagnostics["zero_gain_rate"],
                "threshold": self.config.acceptance_max_zero_gain_rate,
                "passed": query_diagnostics["zero_gain_rate"]
                <= self.config.acceptance_max_zero_gain_rate,
            },
            "max_consecutive_zero_gain": {
                "value": query_diagnostics["max_consecutive_zero_gain"],
                "threshold": self.config.acceptance_max_consecutive_zero_gain,
                "passed": query_diagnostics["max_consecutive_zero_gain"]
                <= self.config.acceptance_max_consecutive_zero_gain,
            },
            "max_consecutive_meaningful_zero_gain": {
                "value": query_diagnostics[
                    "max_consecutive_meaningful_zero_gain"
                ],
                "threshold": self.config.acceptance_max_consecutive_meaningful_zero_gain,
                "passed": query_diagnostics[
                    "max_consecutive_meaningful_zero_gain"
                ]
                <= self.config.acceptance_max_consecutive_meaningful_zero_gain,
            },
            "anchor_query_adherence_rate": {
                "value": anchor_diagnostics["query_anchor_adherence_rate"],
                "threshold": self.config.acceptance_min_anchor_query_adherence,
                "passed": anchor_diagnostics["query_anchor_adherence_rate"]
                >= self.config.acceptance_min_anchor_query_adherence,
            },
            "both_post_seed_modes_observed": {
                "value": int(mode_diagnostics["both_post_seed_modes_observed"]),
                "threshold": int(self.config.acceptance_require_both_post_seed_modes),
                "passed": (
                    mode_diagnostics["both_post_seed_modes_observed"]
                    if self.config.acceptance_require_both_post_seed_modes
                    else True
                ),
            },
            "nonempty_main_response_rate": {
                "value": query_diagnostics["nonempty_main_response_rate"],
                "threshold": 1.0,
                "passed": query_diagnostics["nonempty_main_response_rate"] >= 1.0,
            },
        }
        formal_acceptance["all_passed"] = all(
            item["passed"]
            for item in formal_acceptance.values()
            if isinstance(item, dict)
        )
        return {
            "dataset": self.config.dataset,
            "run_id": self.config.run_id,
            "turns_completed": len(self.turn_records),
            "truth_nodes": len(self.truth.nodes),
            "truth_directed_edge_pairs": len(self.truth.edges),
            "final_graph_nodes": self.graph.number_of_nodes(),
            "final_graph_relation_triples": self.graph.number_of_edges(),
            "mean_htsn": _mean(item["htsn_combined"] for item in batches),
            "mean_count_novelty": _mean(item["count_novelty"] for item in batches),
            "mean_retrospective_gain": _mean(
                item["retrospective_gain"] for item in batches
            ),
            "rotting_diagnostics": rotting_diagnostics(self.arm_controller.rewards),
            "arm_diagnostics": arm_diagnostics,
            "query_diagnostics": query_diagnostics,
            "mode_diagnostics": mode_diagnostics,
            "anchor_diagnostics": anchor_diagnostics,
            "formal_acceptance": formal_acceptance,
            "trajectory": aggregate_trajectory(evaluations),
            "final": final_evaluation,
        }


def _mean(values: Any) -> float:
    materialized = list(values)
    return sum(float(value) for value in materialized) / len(materialized) if materialized else 0.0


def _domain_query(query: str) -> str:
    return query.split("\n\nFor my record", 1)[0].strip()


def _query_tokens(query: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", _domain_query(query).lower()))


def _query_similarity(first: str, second: str) -> float:
    left, right = _query_tokens(first), _query_tokens(second)
    if not left and not right:
        return 1.0
    return len(left & right) / len(left | right) if left | right else 0.0


def _normalized_phrase_present(text: str, phrase: str) -> bool:
    """Match a normalized entity phrase without accepting token substrings."""

    normalized_text = normalize_label(text)
    normalized_phrase = normalize_label(phrase)
    if not normalized_phrase:
        return False
    pattern = rf"(?<![A-Z0-9]){re.escape(normalized_phrase)}(?![A-Z0-9])"
    return re.search(pattern, normalized_text) is not None


def _query_contains_anchor(query: str, anchor: str) -> bool:
    """Check only the domain query, excluding the fixed extraction command."""

    return _normalized_phrase_present(_domain_query(query), anchor)


def _query_signature(query: str) -> str:
    return " ".join(sorted(_query_tokens(query)))


def _query_generation_metadata(
    *,
    query: str,
    source: str,
    attempts: int,
    max_similarity: float,
    similarity_rejections: int,
    anchor_required: bool,
    anchor_present: bool | None,
    anchor_rejections: int,
    fallback_reason: str,
    generation_error_attempts: int = 0,
    last_generation_error: str | None = None,
) -> dict[str, Any]:
    """Return a stable schema for generated and fallback queries."""

    return {
        "source": source,
        "attempts": attempts,
        # Keep the original key for old CSV consumers.
        "rejected_similar_queries": similarity_rejections,
        "similarity_rejected_queries": similarity_rejections,
        "max_similarity": max_similarity,
        "anchor_required": anchor_required,
        "anchor_present": anchor_present,
        "anchor_rejected_queries": anchor_rejections,
        "fallback_reason": fallback_reason,
        "generation_error_attempts": generation_error_attempts,
        "last_generation_error": last_generation_error,
        "domain_query_signature": _query_signature(query),
    }


def _response_anchor_diagnostics(
    *,
    anchor: str | None,
    response: str,
    batch: CandidateBatch,
) -> dict[str, Any]:
    """Audit whether an exploit response actually returns anchor relations."""

    if anchor is None:
        return {
            "anchor_required": False,
            "anchor_in_response_text": None,
            "anchor_in_candidate_nodes": None,
            "anchor_incident_candidate_edges": 0,
            "anchor_response_adherent": None,
        }

    normalized_anchor = normalize_label(anchor)
    incident_edges = sum(
        edge.source == normalized_anchor or edge.target == normalized_anchor
        for edge in batch.edges
    )
    return {
        "anchor_required": True,
        "anchor_in_response_text": _normalized_phrase_present(response, anchor),
        "anchor_in_candidate_nodes": normalized_anchor in batch.nodes,
        "anchor_incident_candidate_edges": incident_edges,
        # A node mention without a relationship is not a successful exploit pull.
        "anchor_response_adherent": incident_edges > 0,
    }


def _effective_fewa_reward(
    *,
    anchor: str | None,
    raw_batch_reward: float,
    anchor_diagnostics: Mapping[str, Any],
) -> float | None:
    """Conservatively credit reward only to an anchor-adherent exploit pull."""

    if anchor is None:
        return None
    return (
        float(raw_batch_reward)
        if anchor_diagnostics.get("anchor_response_adherent") is True
        else 0.0
    )


def _query_diagnostics(
    queries: list[Mapping[str, Any]], turns: list[Mapping[str, Any]]
) -> dict[str, Any]:
    signatures = [_query_signature(str(entry["query"])) for entry in queries]
    unique_queries = len(set(signatures))
    graph_gains: list[bool] = []
    relation_gains: list[bool] = []
    sensitive_gains: list[bool] = []
    meaningful_gains: list[bool] = []
    for record in turns:
        batch = record.get("batch", {})
        gain = record.get("gain", {})
        graph_gain = bool(
            gain.get(
                "graph",
                bool(batch.get("new_nodes", 0) or batch.get("new_edges", 0)),
            )
        )
        relation_gain = bool(
            gain.get("relation", bool(batch.get("new_edges", 0)))
        )
        sensitive_gain = bool(
            gain.get("sensitive", float(batch.get("y_ha", 0.0)) > 0.0)
        )
        meaningful_gain = bool(
            gain.get("meaningful", relation_gain or sensitive_gain)
        )
        graph_gains.append(graph_gain)
        relation_gains.append(relation_gain)
        sensitive_gains.append(sensitive_gain)
        meaningful_gains.append(meaningful_gain)

    zero_graph_gain = [not value for value in graph_gains]
    zero_relation_gain = [not value for value in relation_gains]
    zero_sensitive_gain = [not value for value in sensitive_gains]
    zero_meaningful_gain = [not value for value in meaningful_gains]
    anchor_counts: dict[str, int] = {}
    for entry in queries:
        anchor = entry.get("anchor")
        if anchor:
            anchor_counts[str(anchor)] = anchor_counts.get(str(anchor), 0) + 1
    repeated = {anchor: count for anchor, count in anchor_counts.items() if count >= 2}
    total = len(queries)
    response_nonempty = [
        int(record.get("parser", {}).get("response_characters", 0)) > 0
        for record in turns
    ]
    fallback_turns = sum(
        entry.get("query_generation", {}).get("source")
        == "diversified_fallback"
        for entry in queries
    )
    return {
        "total_queries": total,
        "unique_queries": unique_queries,
        "query_unique_rate": unique_queries / total if total else 0.0,
        # Historical field names retain graph-gain semantics for result continuity.
        "zero_gain_turns": sum(zero_graph_gain),
        "zero_gain_rate": _rate(zero_graph_gain),
        "max_consecutive_zero_gain": _longest_true_streak(zero_graph_gain),
        "zero_graph_gain_turns": sum(zero_graph_gain),
        "zero_graph_gain_rate": _rate(zero_graph_gain),
        "zero_relation_gain_turns": sum(zero_relation_gain),
        "zero_relation_gain_rate": _rate(zero_relation_gain),
        "zero_sensitive_gain_turns": sum(zero_sensitive_gain),
        "zero_sensitive_gain_rate": _rate(zero_sensitive_gain),
        "zero_meaningful_gain_turns": sum(zero_meaningful_gain),
        "zero_meaningful_gain_rate": _rate(zero_meaningful_gain),
        "max_consecutive_meaningful_zero_gain": _longest_true_streak(
            zero_meaningful_gain
        ),
        "repeated_arms": len(repeated),
        "repeated_arm_counts": repeated,
        "nonempty_main_responses": sum(response_nonempty),
        "nonempty_main_response_rate": _rate(response_nonempty),
        "query_generator_fallback_turns": fallback_turns,
        "query_generator_fallback_rate": fallback_turns / total if total else 0.0,
    }


def _rate(values: list[bool]) -> float:
    return sum(values) / len(values) if values else 0.0


def _longest_true_streak(values: list[bool]) -> int:
    longest = current = 0
    for value in values:
        current = current + 1 if value else 0
        longest = max(longest, current)
    return longest


def _arm_diagnostics(state: Mapping[str, Any]) -> dict[str, Any]:
    """Summarize admission separately from actual arm selections."""

    policy = str(state.get("policy", state.get("admission_policy", "unknown")))
    admissions = list(state.get("admission_history", []))
    selections = list(state.get("selection_history", []))
    if not selections and state.get("decisions"):
        selections = [
            {
                "selected_arm": record.get("selected_arm"),
                "epoch_id": None,
                "exploit_pull": record.get("details", {}).get("exploit_pull"),
            }
            for record in state.get("decisions", [])
        ]

    admitted = {
        str(arm)
        for admission in admissions
        for arm in admission.get("active_arms", [])
    }
    selected = {
        str(record["selected_arm"])
        for record in selections
        if record.get("selected_arm")
    }
    delays: list[int] = []
    unqueried_slots = 0
    per_epoch: list[dict[str, Any]] = []
    for admission in admissions:
        epoch_id = admission.get("epoch_id")
        start = int(admission.get("exploit_pull_start", 0))
        epoch_selections = [
            record
            for record in selections
            if record.get("epoch_id") == epoch_id and record.get("selected_arm")
        ]
        epoch_delays: dict[str, int | None] = {}
        for arm in admission.get("active_arms", []):
            matching = [
                int(record.get("exploit_pull", start)) - start
                for record in epoch_selections
                if record.get("selected_arm") == arm
            ]
            delay = min(matching) if matching else None
            epoch_delays[str(arm)] = delay
            if delay is None:
                unqueried_slots += 1
            else:
                delays.append(delay)
        per_epoch.append(
            {
                "epoch_id": epoch_id,
                "active_arms": list(admission.get("active_arms", [])),
                "admission_to_first_query_delay": epoch_delays,
            }
        )

    turnovers: list[float] = []
    for previous, current in zip(admissions, admissions[1:]):
        left = set(previous.get("active_arms", []))
        right = set(current.get("active_arms", []))
        union = left | right
        turnovers.append(1.0 - len(left & right) / len(union) if union else 0.0)

    return {
        "policy": policy,
        "epochs": len(admissions),
        "unique_admitted_arms": len(admitted),
        "unique_selected_arms": len(selected),
        "selected_arms": sorted(selected),
        "mean_admission_to_first_query_delay": _mean(delays),
        "unqueried_admitted_slots": unqueried_slots,
        "mean_epoch_arm_set_turnover": _mean(turnovers),
        "per_epoch": per_epoch,
    }


def _mode_diagnostics(turns: list[Mapping[str, Any]]) -> dict[str, Any]:
    seed_count = sum(
        record.get("decision_reason") == "seed_turn" for record in turns
    )
    post_seed = [
        record
        for record in turns
        if record.get("decision_reason") != "seed_turn"
    ]
    post_seed_counts = Counter(str(record.get("mode", "unknown")) for record in post_seed)
    reason_counts = Counter(
        str(record.get("decision_reason", "unknown")) for record in turns
    )
    by_mode: dict[str, dict[str, float | int]] = {}
    for mode in ("explore", "exploit"):
        records = [record for record in post_seed if record.get("mode") == mode]
        effective_rewards = [
            float(record["effective_fewa_reward"])
            for record in records
            if record.get("effective_fewa_reward") is not None
        ]
        by_mode[mode] = {
            "turns": len(records),
            "mean_htsn": _mean(
                record.get("batch", {}).get("htsn_combined", 0.0)
                for record in records
            ),
            "mean_raw_batch_reward": _mean(
                record.get("raw_batch_reward", record.get("reward", 0.0))
                for record in records
            ),
            "mean_effective_fewa_reward": _mean(effective_rewards),
            "mean_new_nodes": _mean(
                record.get("batch", {}).get("new_nodes", 0) for record in records
            ),
            "mean_new_edges": _mean(
                record.get("batch", {}).get("new_edges", 0) for record in records
            ),
        }

    post_seed_total = len(post_seed)
    return {
        "seed_turns": seed_count,
        "post_seed_turns": post_seed_total,
        "post_seed_explore_turns": post_seed_counts.get("explore", 0),
        "post_seed_exploit_turns": post_seed_counts.get("exploit", 0),
        "post_seed_explore_ratio": (
            post_seed_counts.get("explore", 0) / post_seed_total
            if post_seed_total
            else 0.0
        ),
        "post_seed_exploit_ratio": (
            post_seed_counts.get("exploit", 0) / post_seed_total
            if post_seed_total
            else 0.0
        ),
        "both_post_seed_modes_observed": (
            post_seed_counts.get("explore", 0) > 0
            and post_seed_counts.get("exploit", 0) > 0
        ),
        "decision_reason_counts": dict(sorted(reason_counts.items())),
        "by_mode": by_mode,
    }


def _aggregate_anchor_diagnostics(
    turns: list[Mapping[str, Any]],
) -> dict[str, Any]:
    exploit_turns = [
        record
        for record in turns
        if record.get("mode") == "exploit" and record.get("anchor")
    ]
    query_adherent = [
        bool(record.get("query_generation", {}).get("anchor_present"))
        for record in exploit_turns
    ]
    response_text_hits = [
        bool(record.get("anchor_diagnostics", {}).get("anchor_in_response_text"))
        for record in exploit_turns
    ]
    response_node_hits = [
        bool(record.get("anchor_diagnostics", {}).get("anchor_in_candidate_nodes"))
        for record in exploit_turns
    ]
    response_adherent = [
        bool(record.get("anchor_diagnostics", {}).get("anchor_response_adherent"))
        for record in exploit_turns
    ]
    raw_rewards = [
        float(record.get("raw_batch_reward", record.get("reward", 0.0)))
        for record in exploit_turns
    ]
    effective_rewards = [
        float(record.get("effective_fewa_reward") or 0.0)
        for record in exploit_turns
    ]
    return {
        "eligible_exploit_turns": len(exploit_turns),
        "query_anchor_adherent_turns": sum(query_adherent),
        "query_anchor_adherence_rate": _rate(query_adherent),
        "response_anchor_text_hit_turns": sum(response_text_hits),
        "response_anchor_text_hit_rate": _rate(response_text_hits),
        "response_anchor_node_hit_turns": sum(response_node_hits),
        "response_anchor_node_hit_rate": _rate(response_node_hits),
        "response_anchor_adherent_turns": sum(response_adherent),
        "response_anchor_adherence_rate": _rate(response_adherent),
        "reward_attribution_warning_turns": sum(not value for value in response_adherent),
        "mean_raw_exploit_reward": _mean(raw_rewards),
        "mean_effective_fewa_reward": _mean(effective_rewards),
        "anchor_rejected_query_generations": sum(
            int(record.get("query_generation", {}).get("anchor_rejected_queries", 0))
            for record in exploit_turns
        ),
    }


def _write_json(path: Path, value: Any) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)


def _flatten(prefix: str, value: Mapping[str, Any], output: dict[str, Any]) -> None:
    for key, item in value.items():
        name = f"{prefix}_{key}" if prefix else key
        if isinstance(item, Mapping):
            # Per-node/edge details stay in JSON; CSV contains scalar curves only.
            continue
        if isinstance(item, (str, int, float, bool)) or item is None:
            output[name] = item


def _write_flat_csv(path: Path, records: list[Mapping[str, Any]]) -> None:
    rows: list[dict[str, Any]] = []
    for record in records:
        row: dict[str, Any] = {}
        for key, value in record.items():
            if isinstance(value, Mapping):
                _flatten(key, value, row)
            elif isinstance(value, (str, int, float, bool)) or value is None:
                row[key] = value
        rows.append(row)
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _render_results(summary: Mapping[str, Any], turns: list[Mapping[str, Any]]) -> str:
    final = summary.get("final", {})
    mode_diagnostics = summary.get("mode_diagnostics", {})
    anchor_diagnostics = summary.get("anchor_diagnostics", {})
    arm_diagnostics = summary.get("arm_diagnostics", {})
    lines = [
        "# Medical extraction results",
        "",
        f"- Run: `{summary['run_id']}`",
        f"- Turns: {summary['turns_completed']}",
        f"- Recovered graph: {summary['final_graph_nodes']} nodes / "
        f"{summary['final_graph_relation_triples']} relation triples",
        f"- Node precision: {float(final.get('node_precision', 0.0)):.4f}",
        f"- Node recall: {float(final.get('node_recall', 0.0)):.4f}",
        "- Directed edge-pair precision: "
        f"{float(final.get('edge_pair_precision', 0.0)):.4f}",
        f"- Directed edge-pair recall: {float(final.get('edge_pair_recall', 0.0)):.4f}",
        f"- Node TSC (rank): {float(final.get('node_tsc_rank', 0.0)):.4f}",
        f"- Edge TSC (rank): {float(final.get('edge_tsc_rank', 0.0)):.4f}",
        "- AUTSC, node rank: "
        f"{float(summary.get('trajectory', {}).get('au_node_tsc_rank', 0.0)):.4f}",
        "- AUTSC, edge rank: "
        f"{float(summary.get('trajectory', {}).get('au_edge_tsc_rank', 0.0)):.4f}",
        f"- Mean HTSN: {float(summary['mean_htsn']):.4f}",
        f"- Mean count novelty: {float(summary['mean_count_novelty']):.4f}",
        "- Post-seed explore/exploit: "
        f"{int(mode_diagnostics.get('post_seed_explore_turns', 0))}/"
        f"{int(mode_diagnostics.get('post_seed_exploit_turns', 0))}",
        "- Exploit query anchor adherence: "
        f"{float(anchor_diagnostics.get('query_anchor_adherence_rate', 0.0)):.4f}",
        "- Exploit response anchor adherence: "
        f"{float(anchor_diagnostics.get('response_anchor_adherence_rate', 0.0)):.4f}",
        "",
        "| Turn | Mode | Reason | Anchor | HTSN | Raw reward | Effective FEWA | "
        "Anchor response | Node TSC | Edge TSC |",
        "|---:|---|---|---|---:|---:|---:|---|---:|---:|",
    ]
    for record in turns:
        batch = record["batch"]
        evaluation = record["evaluation"]
        effective_reward = record.get("effective_fewa_reward")
        effective_text = (
            f"{float(effective_reward):.4f}" if effective_reward is not None else "-"
        )
        response_adherent = record.get("anchor_diagnostics", {}).get(
            "anchor_response_adherent"
        )
        response_text = (
            "yes" if response_adherent is True else "no" if response_adherent is False else "-"
        )
        lines.append(
            f"| {record['turn']} | {record['mode']} | {record['decision_reason']} | "
            f"{record['anchor'] or '-'} | {batch['htsn_combined']:.4f} | "
            f"{float(record.get('raw_batch_reward', record.get('reward', 0.0))):.4f} | "
            f"{effective_text} | {response_text} | "
            f"{evaluation['node_tsc_rank']:.4f} | {evaluation['edge_tsc_rank']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Arm-policy diagnostics",
            "",
            f"- Policy: `{arm_diagnostics.get('policy', 'unknown')}`",
            f"- Epochs: {int(arm_diagnostics.get('epochs', 0))}",
            "- Unique admitted / selected arms: "
            f"{int(arm_diagnostics.get('unique_admitted_arms', 0))} / "
            f"{int(arm_diagnostics.get('unique_selected_arms', 0))}",
            "- Selected arms: "
            f"{', '.join(arm_diagnostics.get('selected_arms', [])) or '-'}",
            "- Mean admission-to-first-query delay: "
            f"{float(arm_diagnostics.get('mean_admission_to_first_query_delay', 0.0)):.4f}",
            "- Unqueried admitted slots: "
            f"{int(arm_diagnostics.get('unqueried_admitted_slots', 0))}",
            "- Mean epoch arm-set turnover: "
            f"{float(arm_diagnostics.get('mean_epoch_arm_set_turnover', 0.0)):.4f}",
        ]
    )
    per_epoch = list(arm_diagnostics.get("per_epoch", []))
    if per_epoch:
        lines.extend(
            [
                "",
                "| Epoch | Active arms | Admission-to-first-query delay |",
                "|---:|---|---|",
            ]
        )
        for epoch in per_epoch:
            active = ", ".join(str(arm) for arm in epoch.get("active_arms", []))
            delays = ", ".join(
                f"{arm}: {'unqueried' if delay is None else delay}"
                for arm, delay in epoch.get(
                    "admission_to_first_query_delay", {}
                ).items()
            )
            lines.append(
                f"| {epoch.get('epoch_id', '-')} | {active or '-'} | {delays or '-'} |"
            )
    lines.extend(
        [
            "",
            "## Protocol acceptance",
            "",
            "| Criterion | Value | Threshold | Passed |",
            "|---|---:|---:|---|",
        ]
    )
    acceptance = summary.get("formal_acceptance", {})
    for name in (
        "query_unique_rate",
        "zero_gain_rate",
        "max_consecutive_zero_gain",
        "max_consecutive_meaningful_zero_gain",
        "anchor_query_adherence_rate",
        "both_post_seed_modes_observed",
        "nonempty_main_response_rate",
    ):
        item = acceptance.get(name, {})
        lines.append(
            f"| {name} | {float(item.get('value', 0.0)):.4f} | "
            f"{float(item.get('threshold', 0.0)):.4f} | "
            f"{'yes' if item.get('passed', False) else 'no'} |"
        )
    lines.extend(
        [
            "",
            f"All formal acceptance criteria passed: "
            f"{'yes' if acceptance.get('all_passed', False) else 'no'}.",
            "",
            "HTSN is scored against the graph snapshot before each batch. RTSN is computed after "
            "the merge, and their difference is reported as retrospective gain. GraphRAG truth "
            "does not expose a structured relation type, so truth edge metrics use "
            "directed endpoint pairs; extraction novelty still uses relation triples.",
            "",
        ]
    )
    return "\n".join(lines)
