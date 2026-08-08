"""Configuration loading for reproducible extraction experiments."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping

import yaml


EXTRACTION_DIR = Path(__file__).resolve().parent
PROJECT_DIR = EXTRACTION_DIR.parents[1]


@dataclass
class ExperimentConfig:
    dataset: str = "medical"
    graph_root: str = str(PROJECT_DIR / "artifacts" / "graphrag" / "medical")
    data_dir: str = str(PROJECT_DIR / "artifacts" / "graphrag" / "medical" / "output")
    output_root: str = str(PROJECT_DIR / "artifacts" / "runs" / "mematk")
    run_id: str = "medical_ts_pl_fewa_50turn"
    turns: int = 50
    query_method: str = "local"
    enable_graph_filter: bool = False
    graph_filter_model: str = "gpt-4o-mini"
    initial_epsilon: float = 0.30
    epsilon_decay: float = 0.98
    min_epsilon: float = 0.05
    htsn_threshold: float = 0.15
    htsn_window: int = 5
    adaptive_htsn_threshold: bool = True
    explore_success_window: int = 20
    explore_success_min_samples: int = 5
    explore_success_threshold: float = 0.20
    max_consecutive_failed_explore: int = 2
    random_seed: int = 42
    fewa_delta: float = 0.05
    fewa_max_arms: int = 20
    reward_normalizer: int = 512
    query_generator_model: str = "gpt-4o-mini"
    query_generation_retries: int = 3
    query_similarity_threshold: float = 0.85
    require_exploit_anchor_in_query: bool = True
    acceptance_min_query_unique_rate: float = 0.90
    acceptance_max_zero_gain_rate: float = 0.20
    acceptance_max_consecutive_zero_gain: int = 4
    acceptance_min_anchor_query_adherence: float = 1.0
    acceptance_max_consecutive_meaningful_zero_gain: int = 4
    acceptance_require_both_post_seed_modes: bool = True
    seed_query: str = (
        "Identify major diseases, treatments, diagnostic tests, drugs, symptoms, "
        "risk factors, and care organizations in the medical corpus, and explain "
        "their concrete relationships."
    )
    exploration_queries: list[str] = field(
        default_factory=lambda: [
            (
                "Identify diseases and their treatments, complications, and care "
                "teams in the medical corpus."
            ),
            (
                "Identify diagnostic tests, biomarkers, symptoms, and the conditions "
                "they diagnose in the medical corpus."
            ),
            (
                "Identify drugs and therapies, including indications, side effects, "
                "contraindications, and alternatives."
            ),
            (
                "Identify anatomy, genes, risk factors, and prevention or screening "
                "relationships in the medical corpus."
            ),
            (
                "Identify clinical organizations, professional roles, patient "
                "resources, and their care relationships."
            ),
        ]
    )
    @classmethod
    def load(cls, path: str | Path | None = None) -> "ExperimentConfig":
        config = cls()
        if path is None:
            return config
        with Path(path).open("r", encoding="utf-8") as handle:
            values = yaml.safe_load(handle) or {}
        if not isinstance(values, Mapping):
            raise ValueError("Experiment configuration must be a YAML mapping.")
        unknown = set(values) - set(asdict(config))
        if unknown:
            raise ValueError(f"Unknown configuration fields: {sorted(unknown)}")
        for key, value in values.items():
            setattr(config, key, value)
        return config

    def validate(self) -> None:
        if self.dataset != "medical":
            raise ValueError("This runner currently supports the medical GraphRAG dataset only.")
        if self.turns <= 0:
            raise ValueError("turns must be positive")
        if not 0.0 <= self.htsn_threshold <= 1.0:
            raise ValueError("htsn_threshold must be in [0, 1]")
        if not 0.0 <= self.initial_epsilon <= 1.0:
            raise ValueError("initial_epsilon must be in [0, 1]")
        if not 0.0 <= self.min_epsilon <= 1.0:
            raise ValueError("min_epsilon must be in [0, 1]")
        if not 0.0 < self.epsilon_decay <= 1.0:
            raise ValueError("epsilon_decay must be in (0, 1]")
        if self.reward_normalizer <= 0:
            raise ValueError("reward_normalizer must be positive")
        for name in (
            "explore_success_threshold",
            "query_similarity_threshold",
            "acceptance_min_query_unique_rate",
            "acceptance_max_zero_gain_rate",
            "acceptance_min_anchor_query_adherence",
        ):
            value = float(getattr(self, name))
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0, 1]")
        for name in (
            "explore_success_window",
            "explore_success_min_samples",
            "max_consecutive_failed_explore",
            "query_generation_retries",
            "acceptance_max_consecutive_zero_gain",
            "acceptance_max_consecutive_meaningful_zero_gain",
        ):
            if int(getattr(self, name)) < 0:
                raise ValueError(f"{name} must be non-negative")
        if self.fewa_max_arms <= 0:
            raise ValueError("fewa_max_arms must be positive")
        for required in (self.graph_root, self.data_dir):
            if not Path(required).exists():
                raise FileNotFoundError(required)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
