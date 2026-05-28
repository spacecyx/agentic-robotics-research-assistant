"""
Robotics-aware tag-prior reranker.

This reranker only uses metadata already attached to chunks. It does not call
an LLM and does not change first-stage retrieval; it applies a deterministic
domain prior to the candidate list returned by an existing retriever.
"""

from __future__ import annotations

import re

from app.tools.query_understanding import (
    classify_query_intent,
    compute_section_prior_score,
    get_preferred_sections,
)
from app.tools.robotics_schema import extract_robotics_tags, flatten_robotics_tags
from app.tools.retrievers.schemas import RetrievalResult


ROBOTICS_CATEGORIES_BY_INTENT: dict[str, list[str]] = {
    "sensor": ["sensor_modality"],
    "dataset": ["dataset"],
    "metric": ["metric"],
    "deployment": ["deployment_constraint", "metric"],
    "pipeline": ["system_module", "task_type"],
    "method": ["system_module", "task_type"],
    "architecture": ["system_module", "task_type"],
    "implementation": ["deployment_constraint", "system_module"],
    "robotics_task": ["task_type", "system_module"],
    "experiment": ["dataset", "metric"],
    "result": ["metric", "dataset"],
}


class RoboticsTagPriorReranker:
    """
    Blend retriever score, section prior, and robotics tag prior.

    final_score = retrieval_weight * original_score
                + section_weight * section_prior_score
                + robotics_weight * robotics_tag_score
    """

    def __init__(self, retrieval_weight: float = 0.7):
        if not 0.0 <= retrieval_weight <= 1.0:
            raise ValueError("retrieval_weight must be between 0.0 and 1.0.")

        self.retrieval_weight = retrieval_weight
        remaining_weight = 1.0 - retrieval_weight
        self.section_weight = remaining_weight * 0.35
        self.robotics_weight = remaining_weight * 0.65

    def rerank(
        self,
        query: str,
        results: list[RetrievalResult],
        top_k: int = 5,
    ) -> list[RetrievalResult]:
        if not query.strip():
            raise ValueError("Query must not be empty.")

        if not results:
            return []

        top_k = max(1, min(top_k, len(results)))

        query_intent = classify_query_intent(query)
        preferred_sections = get_preferred_sections(query_intent)
        query_robotics_tags = extract_robotics_tags(query)
        query_flat_tags = set(flatten_robotics_tags(query_robotics_tags))
        preferred_categories = ROBOTICS_CATEGORIES_BY_INTENT.get(query_intent, [])

        reranked_results: list[RetrievalResult] = []

        for index, result in enumerate(results, start=1):
            chunk = result.chunk
            section_title = getattr(chunk, "section_title", None)
            section_prior_score = compute_section_prior_score(
                section_title=section_title,
                preferred_sections=preferred_sections,
            )
            robotics_tag_score, matched_robotics_tags = compute_robotics_tag_score(
                query=query,
                chunk_robotics_tags=getattr(chunk, "robotics_tags", {}) or {},
                query_flat_tags=query_flat_tags,
                preferred_categories=preferred_categories,
            )

            original_score = float(result.score)
            final_score = (
                self.retrieval_weight * original_score
                + self.section_weight * section_prior_score
                + self.robotics_weight * robotics_tag_score
            )

            metadata = dict(result.metadata)
            metadata["original_score"] = original_score
            metadata["query_intent"] = query_intent
            metadata["section_title"] = section_title
            metadata["section_prior_score"] = float(section_prior_score)
            metadata["matched_robotics_tags"] = matched_robotics_tags
            metadata["robotics_tag_score"] = float(robotics_tag_score)
            metadata["final_score"] = float(final_score)
            metadata["rerank_score"] = float(final_score)
            metadata["retrieval_weight"] = self.retrieval_weight
            metadata["section_weight"] = self.section_weight
            metadata["robotics_weight"] = self.robotics_weight
            metadata["rank_before_rerank"] = result.metadata.get("rank", index)
            metadata["reranker"] = "robotics_tag_prior"

            reranked_results.append(
                RetrievalResult(
                    chunk=chunk,
                    score=float(final_score),
                    source=(
                        f"{result.source}+robotics_tag_prior_rerank"
                        if result.source
                        else "robotics_tag_prior_rerank"
                    ),
                    metadata=metadata,
                )
            )

        reranked_results.sort(
            key=lambda item: (
                item.score,
                item.metadata.get("robotics_tag_score", 0.0),
                item.metadata.get("original_score", 0.0),
            ),
            reverse=True,
        )

        for rank, result in enumerate(reranked_results, start=1):
            result.metadata["rank"] = rank

        return reranked_results[:top_k]


def compute_robotics_tag_score(
    query: str,
    chunk_robotics_tags: dict[str, list[str]],
    query_flat_tags: set[str],
    preferred_categories: list[str],
) -> tuple[float, list[str]]:
    if not chunk_robotics_tags:
        return 0.0, []

    matched_tags: list[str] = []
    score = 0.0
    query_terms = _tokenize_query(query)

    for category, tag_names in chunk_robotics_tags.items():
        if not isinstance(tag_names, list):
            continue

        for tag_name in tag_names:
            flat_tag = f"{category}:{tag_name}"
            tag_score = 0.0

            if flat_tag in query_flat_tags:
                tag_score = max(tag_score, 1.0)
            elif _tag_mentions_query(tag_name, query_terms):
                tag_score = max(tag_score, 0.9)

            if category in preferred_categories:
                tag_score = max(tag_score, 0.45)

            if tag_score > 0.0:
                matched_tags.append(flat_tag)
                score += tag_score

    if not matched_tags:
        return 0.0, []

    normalizer = max(1, min(len(matched_tags), 4))
    return min(score / normalizer, 1.0), matched_tags


def _tokenize_query(query: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", query.lower()))


def _tag_mentions_query(tag_name: str, query_terms: set[str]) -> bool:
    tag_terms = set(re.findall(r"[a-z0-9]+", tag_name.lower()))

    if not tag_terms:
        return False

    return bool(tag_terms & query_terms)
