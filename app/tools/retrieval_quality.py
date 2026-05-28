"""
Rule-based retrieval quality scoring.

This module is intentionally independent from the LangGraph workflow. It
summarizes whether the retrieved evidence looks sufficient enough to proceed,
or whether a later conditional branch should expand the query or fallback.
"""

from __future__ import annotations

from typing import Any

from app.tools.query_understanding import classify_query_intent


MIN_TOP_SCORE = 0.05
MIN_AVG_SCORE = 0.03
MIN_CHUNK_COVERAGE_RATIO = 0.5

EXPERIMENT_SECTION_KEYWORDS = (
    "experiment",
    "experimental",
    "evaluation",
    "result",
    "benchmark",
)

DATASET_METRIC_INTENTS = {
    "dataset",
    "metric",
    "experiment",
    "result",
}


def evaluate_retrieval_quality(
    query: str,
    retrieved_chunks: list[Any],
    top_k: int,
    query_intent: str | None = None,
) -> dict[str, Any]:
    """
    Evaluate retrieved evidence quality with conservative rules.

    ``retrieved_chunks`` is expected to be a list of RetrievalResult-like
    objects, but the implementation uses getattr so tests can pass lightweight
    objects.
    """

    intent = query_intent or classify_query_intent(query)
    num_chunks = len(retrieved_chunks)

    if num_chunks == 0:
        return {
            "quality_label": "empty",
            "num_chunks": 0,
            "top_score": None,
            "avg_score": None,
            "section_coverage": _empty_section_coverage(),
            "robotics_tag_coverage": _empty_robotics_tag_coverage(),
            "reasons": ["no_retrieved_chunks"],
            "recommended_action": "fallback",
        }

    scores = [_get_score(item) for item in retrieved_chunks]
    top_score = max(scores) if scores else None
    avg_score = sum(scores) / len(scores) if scores else None
    section_coverage = _summarize_section_coverage(retrieved_chunks)
    robotics_tag_coverage = _summarize_robotics_tag_coverage(retrieved_chunks)

    reasons: list[str] = []

    if top_k > 0 and num_chunks < max(1, int(top_k * MIN_CHUNK_COVERAGE_RATIO)):
        reasons.append("too_few_chunks")

    if top_score is not None and top_score < MIN_TOP_SCORE:
        reasons.append("low_top_score")

    if avg_score is not None and avg_score < MIN_AVG_SCORE:
        reasons.append("low_avg_score")

    if intent in DATASET_METRIC_INTENTS:
        if not section_coverage["has_experiment_like_section"]:
            reasons.append("missing_experiment_or_result_section")

        if (
            robotics_tag_coverage["category_counts"].get("dataset", 0) == 0
            and robotics_tag_coverage["category_counts"].get("metric", 0) == 0
        ):
            reasons.append("missing_dataset_or_metric_tags")

    if intent == "sensor" and robotics_tag_coverage["category_counts"].get("sensor_modality", 0) == 0:
        reasons.append("missing_sensor_tags")

    if reasons:
        return {
            "quality_label": "weak",
            "num_chunks": num_chunks,
            "top_score": top_score,
            "avg_score": avg_score,
            "section_coverage": section_coverage,
            "robotics_tag_coverage": robotics_tag_coverage,
            "reasons": reasons,
            "recommended_action": "expand_query",
        }

    return {
        "quality_label": "good",
        "num_chunks": num_chunks,
        "top_score": top_score,
        "avg_score": avg_score,
        "section_coverage": section_coverage,
        "robotics_tag_coverage": robotics_tag_coverage,
        "reasons": ["sufficient_retrieval_evidence"],
        "recommended_action": "proceed",
    }


def _get_score(item: Any) -> float:
    try:
        return float(getattr(item, "score", 0.0) or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _get_chunk(item: Any) -> Any:
    return getattr(item, "chunk", item)


def _empty_section_coverage() -> dict[str, Any]:
    return {
        "sections": [],
        "section_counts": {},
        "has_experiment_like_section": False,
    }


def _summarize_section_coverage(retrieved_chunks: list[Any]) -> dict[str, Any]:
    section_counts: dict[str, int] = {}

    for item in retrieved_chunks:
        chunk = _get_chunk(item)
        section_title = getattr(chunk, "section_title", None) or "Unknown"
        section_counts[section_title] = section_counts.get(section_title, 0) + 1

    sections = list(section_counts.keys())
    has_experiment_like_section = any(
        any(keyword in section.lower() for keyword in EXPERIMENT_SECTION_KEYWORDS)
        for section in sections
    )

    return {
        "sections": sections,
        "section_counts": section_counts,
        "has_experiment_like_section": has_experiment_like_section,
    }


def _empty_robotics_tag_coverage() -> dict[str, Any]:
    return {
        "tagged_chunks": 0,
        "category_counts": {},
        "flat_tag_counts": {},
    }


def _summarize_robotics_tag_coverage(retrieved_chunks: list[Any]) -> dict[str, Any]:
    tagged_chunks = 0
    category_counts: dict[str, int] = {}
    flat_tag_counts: dict[str, int] = {}

    for item in retrieved_chunks:
        chunk = _get_chunk(item)
        robotics_tags = getattr(chunk, "robotics_tags", {}) or {}
        robotics_flat_tags = getattr(chunk, "robotics_flat_tags", []) or []

        if robotics_tags:
            tagged_chunks += 1

        for category, values in robotics_tags.items():
            if not values:
                continue
            category_counts[category] = category_counts.get(category, 0) + len(values)

        for flat_tag in robotics_flat_tags:
            flat_tag_counts[flat_tag] = flat_tag_counts.get(flat_tag, 0) + 1

    return {
        "tagged_chunks": tagged_chunks,
        "category_counts": category_counts,
        "flat_tag_counts": flat_tag_counts,
    }
