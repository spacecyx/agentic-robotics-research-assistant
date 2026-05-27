# Section-prior reranker
# Uses query intent and chunk section metadata as a lightweight ranking signal.

from app.tools.query_understanding import (
    classify_query_intent,
    compute_section_prior_score,
    get_preferred_sections,
)
from app.tools.retrievers.schemas import RetrievalResult


class SectionPriorReranker:
    """
    Section Prior Reranker.

    final_score = original_score * retrieval_weight
                + section_prior_score * section_prior_weight

    The section prior is a small deterministic bias. It does not replace the
    first-stage retrieval score.
    """

    def __init__(self, retrieval_weight: float = 0.8):
        if not 0.0 <= retrieval_weight <= 1.0:
            raise ValueError("retrieval_weight must be between 0.0 and 1.0.")

        self.retrieval_weight = retrieval_weight
        self.section_prior_weight = 1.0 - retrieval_weight

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

        reranked_results: list[RetrievalResult] = []

        for index, result in enumerate(results, start=1):
            section_title = getattr(result.chunk, "section_title", None)
            section_prior_score = compute_section_prior_score(
                section_title=section_title,
                preferred_sections=preferred_sections,
            )

            original_score = float(result.score)
            final_score = (
                original_score * self.retrieval_weight
                + section_prior_score * self.section_prior_weight
            )

            metadata = dict(result.metadata)
            metadata["original_score"] = original_score
            metadata["query_intent"] = query_intent
            metadata["section_title"] = section_title
            metadata["section_prior_score"] = float(section_prior_score)
            metadata["rerank_score"] = float(final_score)
            metadata["retrieval_weight"] = self.retrieval_weight
            metadata["section_prior_weight"] = self.section_prior_weight
            metadata["rank_before_rerank"] = result.metadata.get("rank", index)
            metadata["reranker"] = "section_prior"

            reranked_results.append(
                RetrievalResult(
                    chunk=result.chunk,
                    score=float(final_score),
                    source=f"{result.source}+section_prior_rerank" if result.source else "section_prior_rerank",
                    metadata=metadata,
                )
            )

        reranked_results.sort(
            key=lambda item: (
                item.score,
                item.metadata.get("original_score", 0.0),
            ),
            reverse=True,
        )

        for rank, result in enumerate(reranked_results, start=1):
            result.metadata["rank"] = rank

        return reranked_results[:top_k]
