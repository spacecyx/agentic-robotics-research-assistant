# Multi Query Retriever
# 作用：对多个 query variants 分别检索，然后合并、去重、重排候选结果

from __future__ import annotations

from typing import Any

from app.tools.query_expansion import HeuristicQueryExpander
from app.tools.retrievers.base import BaseRetriever
from app.tools.retrievers.schemas import RetrievalResult


class MultiQueryRetriever:
    """
    Multi-query retrieval wrapper.

    它不替代已有 retriever，而是包裹已有 retriever：

    original query
        -> query expansion
        -> multiple retriever.search()
        -> merge + dedup
        -> return RetrievalResult list
    """

    def __init__(
        self,
        base_retriever: BaseRetriever,
        query_expander: HeuristicQueryExpander | None = None,
        max_queries: int = 4,
        per_query_k: int = 10,
        rrf_k: int = 60,
    ):
        if max_queries <= 0:
            raise ValueError("max_queries must be positive.")

        if per_query_k <= 0:
            raise ValueError("per_query_k must be positive.")

        if rrf_k <= 0:
            raise ValueError("rrf_k must be positive.")

        self.base_retriever = base_retriever
        self.query_expander = query_expander or HeuristicQueryExpander()
        self.max_queries = max_queries
        self.per_query_k = per_query_k
        self.rrf_k = rrf_k

        self.last_expanded_queries: list[str] = []

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievalResult]:
        if not query.strip():
            raise ValueError("Query must not be empty.")

        top_k = max(1, top_k)

        expanded_queries = self.query_expander.expand(
            query=query,
            max_queries=self.max_queries,
        )

        self.last_expanded_queries = expanded_queries

        merged: dict[Any, dict[str, Any]] = {}

        for query_index, expanded_query in enumerate(expanded_queries):
            results = self.base_retriever.search(
                query=expanded_query,
                top_k=self.per_query_k,
            )

            for rank, result in enumerate(results, start=1):
                chunk_key = self._get_chunk_key(result.chunk)
                rrf_score = 1.0 / (self.rrf_k + rank)

                if chunk_key not in merged:
                    merged[chunk_key] = {
                        "chunk": result.chunk,
                        "score": 0.0,
                        "source": result.source,
                        "matched_queries": [],
                        "query_indices": [],
                        "original_scores": [],
                        "original_ranks": [],
                        "base_sources": [],
                        "base_metadata": result.metadata,
                    }

                merged_item = merged[chunk_key]
                merged_item["score"] += rrf_score
                merged_item["matched_queries"].append(expanded_query)
                merged_item["query_indices"].append(query_index)
                merged_item["original_scores"].append(float(result.score))
                merged_item["original_ranks"].append(rank)
                merged_item["base_sources"].append(result.source)

        retrieval_results: list[RetrievalResult] = []

        for item in merged.values():
            original_scores = item["original_scores"]
            original_ranks = item["original_ranks"]

            metadata = dict(item["base_metadata"])
            metadata.update(
                {
                    "multi_query": True,
                    "expanded_queries": expanded_queries,
                    "matched_queries": item["matched_queries"],
                    "matched_query_count": len(item["matched_queries"]),
                    "query_indices": item["query_indices"],
                    "original_scores": original_scores,
                    "original_ranks": original_ranks,
                    "best_original_score": max(original_scores) if original_scores else 0.0,
                    "best_original_rank": min(original_ranks) if original_ranks else None,
                    "rrf_k": self.rrf_k,
                    "per_query_k": self.per_query_k,
                }
            )

            base_source = item["source"] or "retriever"

            retrieval_results.append(
                RetrievalResult(
                    chunk=item["chunk"],
                    score=float(item["score"]),
                    source=f"{base_source}+multi_query",
                    metadata=metadata,
                )
            )

        retrieval_results.sort(
            key=lambda result: (
                result.score,
                result.metadata.get("matched_query_count", 0),
                result.metadata.get("best_original_score", 0.0),
            ),
            reverse=True,
        )

        for rank, result in enumerate(retrieval_results, start=1):
            result.metadata["rank"] = rank

        return retrieval_results[:top_k]

    @staticmethod
    def _get_chunk_key(chunk: Any) -> Any:
        if hasattr(chunk, "chunk_id"):
            return getattr(chunk, "chunk_id")

        return id(chunk)