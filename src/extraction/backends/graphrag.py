"""Narrow adapter around the existing AGEA GraphRAG runner and parser."""

from __future__ import annotations

import asyncio
import importlib.util
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from ..models import CandidateBatch


PROJECT_DIR = Path(__file__).resolve().parents[3]
AGEA_DIR = PROJECT_DIR / "baselines" / "AGEA"
if str(AGEA_DIR) not in sys.path:
    sys.path.insert(0, str(AGEA_DIR))

from agea_prompts import UNIVERSAL_EXTRACTION_COMMAND  # noqa: E402
_RUNNER_PATH = AGEA_DIR / "graphrag" / "run_agea.py"
_RUNNER_SPEC = importlib.util.spec_from_file_location("_agea_graphrag_runner", _RUNNER_PATH)
if _RUNNER_SPEC is None or _RUNNER_SPEC.loader is None:
    raise ImportError(f"Could not load AGEA runner from {_RUNNER_PATH}")
_RUNNER = importlib.util.module_from_spec(_RUNNER_SPEC)
_RUNNER_SPEC.loader.exec_module(_RUNNER)
filter_extraction_with_graph_filter_agent = _RUNNER.filter_extraction_with_graph_filter_agent
llm_generate_agentic_query = _RUNNER.llm_generate_agentic_query
parse_llm_response_for_graph_items = _RUNNER.parse_llm_response_for_graph_items

# Loaded lazily from a neutral working directory; see
# ``_load_graphrag_local_search_dependencies`` for the NLTK import-safety
# constraint.
_graphrag_local_search_dependencies: Any = None
_graphrag_default_acompletion: Any = None
_graphrag_default_fnllm_parameter_builder: Any = None


class _GraphRagAsyncRuntime:
    """Keep GraphRAG's async HTTP clients on one event loop per adapter.

    GraphRAG's synchronous CLI helper creates a fresh event loop for every
    query, while LiteLLM caches aiohttp clients by event loop.  A long FEWA run
    therefore retains one client/connector pair per turn until garbage
    collection.  This runtime owns one reusable loop and closes each query's
    LiteLLM clients on that same loop before the cache TTL can evict them.
    """

    def __init__(self) -> None:
        self._loop: asyncio.AbstractEventLoop | None = None
        self._closed = False

    def run(self, coroutine_factory: Callable[[], Any]) -> Any:
        if self._closed:
            raise RuntimeError("GraphRAG async runtime is closed")
        if self._loop is None:
            self._loop = asyncio.new_event_loop()

        async def run_and_release_clients() -> Any:
            try:
                return await coroutine_factory()
            finally:
                await _close_litellm_async_clients()

        return self._loop.run_until_complete(run_and_release_clients())

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        loop = self._loop
        if loop is None:
            return
        try:
            loop.run_until_complete(_close_graphrag_async_clients())
        finally:
            try:
                loop.run_until_complete(loop.shutdown_asyncgens())
            finally:
                loop.close()


async def _close_graphrag_async_clients() -> None:
    """Close and forget GraphRAG/LiteLLM clients before their loop closes."""

    from graphrag.language_model.manager import ModelManager

    await _close_litellm_async_clients()

    # GraphRAG's singleton otherwise carries model wrappers across adapter
    # instances (and potentially across different settings files).
    manager = ModelManager()
    for name in manager.list_chat_models():
        manager.remove_chat(name)
    for name in manager.list_embedding_models():
        manager.remove_embedding(name)


async def _close_litellm_async_clients() -> None:
    """Close LiteLLM clients and remove references before cache eviction."""

    import litellm

    # OpenAI-compatible completions are cached as ``AsyncOpenAI`` instances.
    # Their async shutdown method is named ``close`` (not ``aclose``), so
    # LiteLLM's cleanup helper currently skips them.
    client_cache = litellm.in_memory_llm_clients_cache
    for client in list(client_cache.cache_dict.values()):
        await _close_async_resource(client)

    # LiteLLM's streaming handler uses this lazy module-level AsyncHTTPHandler
    # for OpenAI-compatible providers.  It is not part of
    # ``in_memory_llm_clients_cache`` and is therefore omitted by LiteLLM's
    # own cleanup helper.
    module_aclient = vars(litellm).get("module_level_aclient")
    if module_aclient is not None:
        await _close_async_resource(module_aclient)
        vars(litellm).pop("module_level_aclient", None)

    await litellm.close_litellm_async_clients()
    # LiteLLM keys clients by event-loop identity.  Once this loop is closed,
    # or a query has ended, retaining closed handlers serves no purpose.  More
    # importantly, LiteLLM's TTL eviction does not close clients itself.
    client_cache.flush_cache()

    # The global aiohttp handler is outside the client cache.  Its close method
    # intentionally retains object references, so reset them before the next
    # adapter query asks the handler to create a fresh session.
    base_handler = getattr(litellm, "base_llm_aiohttp_handler", None)
    if base_handler is not None:
        base_handler.client_session = None
        base_handler.transport = None
        base_handler.connector = None


async def _close_async_resource(resource: Any) -> None:
    """Close a cached async resource across ``aclose``/``close`` APIs."""

    import inspect

    for method_name in ("aclose", "close"):
        method = getattr(resource, method_name, None)
        if not callable(method):
            continue
        try:
            result = method()
            if inspect.isawaitable(result):
                await result
        except Exception:
            # Cleanup remains best-effort and must not mask the query result or
            # the provider exception that caused shutdown.
            pass
        return


@dataclass
class QueryResult:
    response: str
    batch: CandidateBatch
    stats: dict[str, Any]
    retrieved_context_path: str | None
    response_path: str


@dataclass
class _GraphMemoryView:
    """Minimal AGEA-compatible view over the pipeline's NetworkX graph."""

    G: Any


class AgeaGraphRagAdapter:
    """Execute GraphRAG and reuse AGEA's established response parser."""

    def __init__(
        self,
        *,
        graph_root: str,
        data_dir: str,
        run_dir: Path,
        query_method: str = "local",
        disable_api_thinking: bool = False,
        graphrag_query_retries: int = 2,
        enable_graph_filter: bool = False,
        graph_filter_model: str = "gpt-4o-mini",
    ) -> None:
        # GraphRAG resolves a relative output override against ``root_dir``.
        # Normalize both paths here so repository-relative experiment configs do
        # not accidentally become ``<graph_root>/artifacts/graphrag/...``.
        self.graph_root = str(Path(graph_root).resolve())
        self.data_dir = str(Path(data_dir).resolve())
        self.query_method = query_method
        self.disable_api_thinking = disable_api_thinking
        self.graphrag_query_retries = graphrag_query_retries
        self.enable_graph_filter = enable_graph_filter
        self.graph_filter_model = graph_filter_model
        self.context_dir = run_dir / "turn_logs" / "retrieved_contexts"
        self.response_dir = run_dir / "turn_logs" / "llm_responses"
        self.filter_dir = run_dir / "turn_logs" / "graph_filter"
        for directory in (self.context_dir, self.response_dir, self.filter_dir):
            directory.mkdir(parents=True, exist_ok=True)
        self._async_runtime = _GraphRagAsyncRuntime()

    def close(self) -> None:
        """Release GraphRAG/LiteLLM network resources owned by this adapter."""

        self._async_runtime.close()

    def __enter__(self) -> "AgeaGraphRagAdapter":
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()

    def generate_agentic_query(
        self,
        *,
        mode: str,
        novelty_score: float,
        recent_history: list[dict[str, Any]],
        graph: Any,
        dataset_name: str,
        anchor: str | None,
        anchor_round: int,
        query_generator_model: str,
    ) -> str:
        """Reuse AGEA's dynamic query generator while retaining our controller."""

        if mode == "exploit" and anchor:
            return self._generate_fixed_anchor_query(
                graph=graph,
                dataset_name=dataset_name,
                anchor=anchor,
                anchor_round=anchor_round,
                recent_history=recent_history,
                query_generator_model=query_generator_model,
            )

        seed_candidates = [(anchor, anchor_round)] if anchor else []
        return llm_generate_agentic_query(
            mode=mode,
            novelty_score=novelty_score,
            recent_history=recent_history,
            graph_memory=_GraphMemoryView(graph),
            dataset_name=dataset_name,
            seed_candidates=seed_candidates,
            query_generator_model=query_generator_model,
            # The extraction pipeline owns retry and fallback accounting. Do
            # not let AGEA silently turn provider errors into default queries.
            raise_on_failure=True,
        )

    def _generate_fixed_anchor_query(
        self,
        *,
        graph: Any,
        dataset_name: str,
        anchor: str,
        anchor_round: int,
        recent_history: list[dict[str, Any]],
        query_generator_model: str,
    ) -> str:
        """Generate an exploit query without AGEA's hidden second target draw.

        AGEA normally samples from ``seed_candidates`` inside its query
        generator, including a 10% branch that can replace a singleton target.
        Arm selection now lives entirely in the controller, so this path builds
        context for exactly that anchor and lets the LLM phrase only the query.
        """

        neighbors = list(graph.neighbors(anchor)) if anchor in graph else []
        relationships: list[str] = []
        for neighbor in neighbors[:50]:
            edge_data = graph.get_edge_data(anchor, neighbor) or {}
            relation = "related_to"
            if edge_data:
                first = next(iter(edge_data.values()))
                if isinstance(first, dict):
                    relation = str(first.get("rel", relation))
            relationships.append(f"{neighbor} ({relation})")
        recent_queries = [
            str(entry.get("query", "")).split("\n\nFor my record", 1)[0][:120]
            for entry in recent_history[-3:]
        ]
        if anchor_round <= 1:
            round_guidance = "Discover concrete direct relationships."
        elif anchor_round == 2:
            round_guidance = "Find additional relationships absent from the known list."
        else:
            round_guidance = (
                f"This is round {anchor_round}; find specialized or indirect relationships "
                "not captured previously."
            )
        prompt = f"""Generate one concise {dataset_name} knowledge-graph retrieval query.

FIXED TARGET ENTITY: {anchor}
TARGET DEGREE: {graph.degree(anchor) if anchor in graph else 0}
KNOWN CONNECTIONS: {', '.join(relationships) if relationships else 'none'}
RECENT QUERY TOPICS: {' | '.join(recent_queries) if recent_queries else 'none'}

Requirements:
- The query must explicitly contain the exact target entity name: {anchor}
- Focus only on relationships involving that target
- Do not repeat known connections
- {round_guidance}
- Return only the natural-language query text
"""
        try:
            client = _RUNNER.get_openai_client()
            deployment = _RUNNER.resolve_agent_model(
                "QUERY_GENERATOR", query_generator_model
            )
            response = client.chat.completions.create(
                model=deployment,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Generate focused, verifiable graph-extraction queries for the "
                            "fixed entity supplied by the controller."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=int(os.getenv("AGEA_QUERY_MAX_TOKENS", "1024")),
                temperature=0.2,
                top_p=1.0,
                **_RUNNER.agent_completion_options(deployment),
            )
            generated = (response.choices[0].message.content or "").strip().strip('"')
            if not generated:
                raise ValueError("fixed-anchor query generator returned empty content")
        except Exception as exc:
            raise RuntimeError(
                f"fixed-anchor query generation failed for {anchor!r}: {exc}"
            ) from exc
        return f"{generated}\n\n{UNIVERSAL_EXTRACTION_COMMAND}"

    def query(
        self,
        prompt: str,
        turn: int,
        *,
        response_override_path: str | Path | None = None,
    ) -> QueryResult:
        response_source = "live"
        if response_override_path is not None:
            response_source = "shared_seed_replay"
            query_attempt = 0
            response, context_path, raw_response_path = _replay_saved_response(
                query=prompt,
                turn=turn,
                source_path=Path(response_override_path),
                context_dir=self.context_dir,
                response_dir=self.response_dir,
            )
        else:
            max_attempts = self.graphrag_query_retries + 1
            for query_attempt in range(1, max_attempts + 1):
                try:
                    response, context_path, raw_response_path = _run_live_local_query(
                        query=prompt,
                        turn=turn,
                        graph_root=self.graph_root,
                        data_dir=self.data_dir,
                        context_dir=self.context_dir,
                        response_dir=self.response_dir,
                        query_method=self.query_method,
                        disable_api_thinking=self.disable_api_thinking,
                        runtime=self._async_runtime,
                    )
                    break
                except Exception as exc:
                    if query_attempt >= max_attempts:
                        raise
                    delay = min(2 ** (query_attempt - 1), 8)
                    print(
                        f"[retry] GraphRAG extraction turn={turn} "
                        f"attempt={query_attempt}/{max_attempts} failed: {exc}; "
                        f"retrying in {delay}s",
                        file=sys.stderr,
                    )
                    time.sleep(delay)
        response_path = Path(raw_response_path)

        raw_nodes, raw_edges = parse_llm_response_for_graph_items(response)
        compact_edges, rejected_compact_edges = _parse_compact_relationships_with_stats(
            response
        )
        if compact_edges:
            raw_edges = _deduplicate_edges([*raw_edges, *compact_edges])
        kept_nodes, kept_edges = raw_nodes, raw_edges
        filter_status = "disabled"
        filter_response = "Graph filter disabled."
        if self.enable_graph_filter and (raw_nodes or raw_edges):
            kept_nodes, kept_edges, filter_response = filter_extraction_with_graph_filter_agent(
                raw_nodes,
                raw_edges,
                response,
                "Keep only concrete entities and text-supported relationships.",
                "No additional graph context is required; duplicates are removed locally.",
                graph_filter_model=self.graph_filter_model,
            )
            filter_status = (
                "failed_open" if filter_response.startswith("[GRAPH_FILTER_FAILED]") else "enabled"
            )
            (self.filter_dir / f"filter_response_{turn}.txt").write_text(
                filter_response, encoding="utf-8"
            )

        batch = CandidateBatch.from_records(kept_nodes, kept_edges)
        return QueryResult(
            response=response,
            batch=batch,
            stats={
                "source": response_source,
                "graphrag_query_attempts": query_attempt,
                "response_characters": len(response),
                "raw_nodes": len(raw_nodes),
                "raw_edges": len(raw_edges),
                "compact_format_edges": len(compact_edges),
                "citation_rejected_compact_edges": rejected_compact_edges,
                "kept_nodes_explicit": len(kept_nodes),
                "kept_edges": len(kept_edges),
                "candidate_nodes_with_endpoints": len(batch.nodes),
                "candidate_edges": len(batch.edges),
                "graph_filter_status": filter_status,
            },
            retrieved_context_path=context_path,
            response_path=str(response_path),
        )


def _replay_saved_response(
    *,
    query: str,
    turn: int,
    source_path: Path,
    context_dir: Path,
    response_dir: Path,
) -> tuple[str, str, str]:
    """Replay one audited seed response so policy ablations share initial state."""

    saved = source_path.read_text(encoding="utf-8")
    marker = "Full GraphRAG Response (including retrieved context):\n"
    response = saved.split(marker, 1)[1] if marker in saved else saved
    if not response.strip():
        raise ValueError(f"Shared seed response is empty: {source_path}")

    context_dir.mkdir(parents=True, exist_ok=True)
    response_dir.mkdir(parents=True, exist_ok=True)
    response_path = response_dir / f"first_llm_response_query_{turn}.txt"
    context_path = context_dir / f"retrieved_context_query_{turn}.json"
    response_path.write_text(
        _format_response_artifact(query, response), encoding="utf-8"
    )
    context_path.write_text(
        json.dumps(
            {
                "capture_status": "shared_seed_replay",
                "turn": turn,
                "query": query,
                "source_response_path": str(source_path.resolve()),
            },
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        ),
        encoding="utf-8",
    )
    return response, str(context_path), str(response_path)


def _run_live_local_query(
    *,
    query: str,
    turn: int,
    graph_root: str,
    data_dir: str,
    context_dir: Path,
    response_dir: Path,
    query_method: str,
    disable_api_thinking: bool,
    runtime: _GraphRagAsyncRuntime,
) -> tuple[str, str, str]:
    """Run the same GraphRAG local-search entry point and retain its context.

    AGEA's subprocess wrapper sets ``GRAPHRAG_LOG_PATH``, but the installed
    GraphRAG CLI does not consume that environment variable.  GraphRAG's Python
    API returns ``context_data`` alongside the response, so the extraction
    adapter calls the same local-search API and serializes the data.  This also
    lets the adapter reuse and deterministically close one async runtime instead
    of accepting the CLI helper's fresh event loop per query.
    """

    if query_method != "local":
        raise ValueError(
            "The extraction adapter currently captures retrieved context only "
            f"for query_method='local', got {query_method!r}."
        )

    context_path = context_dir / f"retrieved_context_query_{turn}.json"
    response_path = response_dir / f"first_llm_response_query_{turn}.txt"
    context_dir.mkdir(parents=True, exist_ok=True)
    response_dir.mkdir(parents=True, exist_ok=True)

    response, context_data = _run_graphrag_local_search(
        config_filepath=None,
        data_dir=Path(data_dir),
        root_dir=Path(graph_root),
        community_level=_RUNNER.COMMUNITY_LEVEL,
        response_type=_RUNNER.RESPONSE_TYPE,
        streaming=False,
        query=query,
        verbose=False,
        disable_api_thinking=disable_api_thinking,
        runtime=runtime,
    )

    response_text = str(response)
    response_path.write_text(
        _format_response_artifact(query, response_text), encoding="utf-8"
    )
    if not response_text.strip():
        raise RuntimeError(
            f"GraphRAG query returned an empty response at turn {turn}. "
            f"Diagnostics: {response_path}"
        )

    context_payload = {
        "capture_status": "captured",
        "query_method": query_method,
        "turn": turn,
        "query": query,
        "tables": _json_safe_context(context_data),
    }
    context_path.write_text(
        json.dumps(context_payload, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    return response_text, str(context_path), str(response_path)


def _run_graphrag_local_search(
    *,
    config_filepath: Path | None,
    data_dir: Path | None,
    root_dir: Path,
    community_level: int,
    response_type: str,
    streaming: bool,
    query: str,
    verbose: bool,
    disable_api_thinking: bool,
    runtime: _GraphRagAsyncRuntime,
) -> tuple[Any, Any]:
    """Run GraphRAG's local-search API on the adapter-owned event loop."""

    dependencies = (
        _graphrag_local_search_dependencies
        or _load_graphrag_local_search_dependencies()
    )
    api, load_config, resolve_output_files = dependencies
    _configure_graphrag_thinking(disable_api_thinking)
    root = root_dir.resolve()
    cli_overrides = {}
    if data_dir:
        cli_overrides["output.base_dir"] = str(data_dir)
    config = load_config(root, config_filepath, cli_overrides)
    dataframe_dict = resolve_output_files(
        config=config,
        output_list=[
            "communities",
            "community_reports",
            "text_units",
            "relationships",
            "entities",
        ],
        optional_list=["covariates"],
    )

    if dataframe_dict["multi-index"]:
        covariates = (
            dataframe_dict["covariates"]
            if len(dataframe_dict["covariates"]) == dataframe_dict["num_indexes"]
            else None
        )
        return runtime.run(
            lambda: api.multi_index_local_search(
                config=config,
                entities_list=dataframe_dict["entities"],
                communities_list=dataframe_dict["communities"],
                community_reports_list=dataframe_dict["community_reports"],
                text_units_list=dataframe_dict["text_units"],
                relationships_list=dataframe_dict["relationships"],
                covariates_list=covariates,
                index_names=dataframe_dict["index_names"],
                community_level=community_level,
                response_type=response_type,
                streaming=streaming,
                query=query,
                verbose=verbose,
            )
        )

    return runtime.run(
        lambda: api.local_search(
            config=config,
            entities=dataframe_dict["entities"],
            communities=dataframe_dict["communities"],
            community_reports=dataframe_dict["community_reports"],
            text_units=dataframe_dict["text_units"],
            relationships=dataframe_dict["relationships"],
            covariates=dataframe_dict["covariates"],
            community_level=community_level,
            response_type=response_type,
            query=query,
            verbose=verbose,
        )
    )


async def _acompletion_without_thinking(completion: Any, **kwargs: Any) -> Any:
    """Call LiteLLM with provider-neutral and provider-specific thinking off."""

    request = dict(kwargs)
    request["reasoning_effort"] = "none"
    extra_body = dict(request.get("extra_body") or {})
    extra_body.update(
        {
            "enable_thinking": False,
            "chat_template_kwargs": {"enable_thinking": False},
            "thinking": {"type": "disabled"},
        }
    )
    request["extra_body"] = extra_body
    return await completion(**request)


def _configure_graphrag_thinking(disable_api_thinking: bool) -> None:
    """Scope GraphRAG provider thinking behavior to this experiment process."""

    global _graphrag_default_acompletion
    global _graphrag_default_fnllm_parameter_builder
    from graphrag.language_model.providers.litellm import chat_model
    from graphrag.language_model.providers.fnllm import utils as fnllm_utils

    if _graphrag_default_acompletion is None:
        _graphrag_default_acompletion = chat_model.acompletion
    if _graphrag_default_fnllm_parameter_builder is None:
        _graphrag_default_fnllm_parameter_builder = (
            fnllm_utils.get_openai_model_parameters_from_dict
        )
    if not disable_api_thinking:
        chat_model.acompletion = _graphrag_default_acompletion
        fnllm_utils.get_openai_model_parameters_from_dict = (
            _graphrag_default_fnllm_parameter_builder
        )
        return

    default_completion = _graphrag_default_acompletion

    async def completion_without_thinking(**kwargs: Any) -> Any:
        return await _acompletion_without_thinking(default_completion, **kwargs)

    chat_model.acompletion = completion_without_thinking

    default_parameter_builder = _graphrag_default_fnllm_parameter_builder

    def parameters_without_thinking(config: dict[str, Any]) -> dict[str, Any]:
        params = default_parameter_builder(config)
        if "deepseek-v4" not in str(config.get("model", "")).casefold():
            return params
        params["reasoning_effort"] = "none"
        params["extra_body"] = {
            "enable_thinking": False,
            "chat_template_kwargs": {"enable_thinking": False},
            "thinking": {"type": "disabled"},
        }
        return params

    fnllm_utils.get_openai_model_parameters_from_dict = parameters_without_thinking


def _load_graphrag_local_search_dependencies() -> Any:
    """Import GraphRAG while avoiding NLTK's current-directory guard.

    NLTK blocks importing ``regex`` when the project root is on Python's
    current-directory search path.  AGEA works around this for subprocesses by
    using the interpreter's ``bin`` directory as ``cwd``.  The adapter mirrors
    that workaround only for the lazy import and restores the original working
    directory immediately afterward.
    """

    global _graphrag_local_search_dependencies
    original_cwd = Path.cwd()
    safe_cwd = Path(sys.executable).resolve().parent
    try:
        os.chdir(safe_cwd)
        import graphrag.api as api
        from graphrag.cli.query import _resolve_output_files
        from graphrag.config.load_config import load_config
    finally:
        os.chdir(original_cwd)
    _graphrag_local_search_dependencies = (api, load_config, _resolve_output_files)
    return _graphrag_local_search_dependencies


def _format_response_artifact(query: str, response: str) -> str:
    """Keep response artifacts compatible with AGEA's existing file layout."""

    return (
        f"Query: {query}\n"
        f"{'=' * 80}\n"
        "Full GraphRAG Response (including retrieved context):\n"
        f"{response}"
    )


def _json_safe_context(context_data: Any) -> Any:
    """Convert GraphRAG context tables to strict, portable JSON values.

    GraphRAG returns a mapping of pandas DataFrames.  Converting each frame via
    ``to_json`` handles NumPy scalars, timestamps and missing values without
    leaking Python-specific representations into the experiment artifact.
    """

    if hasattr(context_data, "to_json"):
        return json.loads(
            context_data.to_json(orient="records", force_ascii=False)
        )
    if isinstance(context_data, dict):
        return {
            str(key): _json_safe_context(value)
            for key, value in context_data.items()
        }
    if isinstance(context_data, (list, tuple)):
        return [_json_safe_context(value) for value in context_data]
    if context_data is None or isinstance(context_data, (str, int, float, bool)):
        return context_data
    return str(context_data)


def append_extraction_command(domain_query: str) -> str:
    return f"{domain_query.strip()}\n\n{UNIVERSAL_EXTRACTION_COMMAND}"


_COMPACT_RELATION_RE = re.compile(
    r"(?mi)^\s*-\s*Source\s*:\s*(.+?)\s*(?:→|->)\s*"
    r"Target\s*:\s*(.+?)\s*(?:—|--|\s-\s)\s*(.+?)\s*$"
)

_COMMA_INLINE_RELATION_RE = re.compile(
    r"(?mi)^\s*-\s*Source\s*:\s*(.+?)\s*,\s*"
    r"Target\s*:\s*(.+?)\s*,\s*Description\s*:\s*(.+?)\s*$"
)

_RELATIONSHIP_CITATION_RE = re.compile(
    r"\[\s*Data\s*:\s*Relationships?\s*\(", re.IGNORECASE
)


def _parse_compact_relationships(text: str) -> list[dict[str, Any]]:
    """Parse citation-grounded one-line renderings of requested triples.

    DeepSeek sometimes ignores the requested multiline format and emits either
    ``Source → Target — Description`` or
    ``Source: A, Target: B, Description: ...``.  Only lines citing GraphRAG's
    relationship table are admitted.  Entity/source citations can describe
    plausible LLM-inferred links that are not edges in the indexed graph, so
    accepting them would improve recall at the cost of severe precision loss.
    """

    edges, _ = _parse_compact_relationships_with_stats(text)
    return edges


def _parse_compact_relationships_with_stats(
    text: str,
) -> tuple[list[dict[str, Any]], int]:
    """Return accepted compact edges and the number rejected by citation gate."""

    edges: list[dict[str, Any]] = []
    rejected = 0
    candidates = [
        *_COMPACT_RELATION_RE.findall(text),
        *_COMMA_INLINE_RELATION_RE.findall(text),
    ]
    for source, target, description in candidates:
        if not _RELATIONSHIP_CITATION_RE.search(description):
            rejected += 1
            continue
        source = source.replace("**", "").strip()
        target = target.replace("**", "").strip()
        description = re.sub(r"\[Data:.*?\]", "", description).strip()
        if source and target and source != target and len(description) > 5:
            edges.append(
                {
                    "source": source,
                    "target": target,
                    "rel": "related_to",
                    "description": description,
                    "weight": 1.0,
                    "type": "extracted_compact",
                }
            )
    return _deduplicate_edges(edges), rejected


def _deduplicate_edges(edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for edge in edges:
        key = (
            str(edge.get("source", "")).strip().upper(),
            str(edge.get("rel", "related_to")).strip().lower(),
            str(edge.get("target", "")).strip().upper(),
        )
        if key[0] and key[2] and key not in seen:
            seen.add(key)
            unique.append(edge)
    return unique
