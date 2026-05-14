# 分数融合 Reranker
# 作用：融合原始检索分数和关键词重排分数 | 保留了原始 Retriever 的排序能力，同时用关键词相关性做二次校正

from app.tools.retrievers.schemas import RetrievalResult
from app.tools.rerankers.base import get_chunk_text
from app.tools.rerankers.keyword_reranker import compute_keyword_score


class ScoreFusionReranker:
    """
    Score Fusion Reranker。

    final_score = retriever_weight * normalized_retriever_score
                + (1 - retriever_weight) * keyword_score

    retriever_weight 越大，越相信原始 Retriever；
    retriever_weight 越小，越相信关键词重排。
    """

    def __init__(self, retriever_weight: float = 0.7):
        if not 0.0 <= retriever_weight <= 1.0:
            raise ValueError("retriever_weight must be between 0.0 and 1.0.")

        self.retriever_weight = retriever_weight

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

        original_scores = {
            index: float(result.score)
            for index, result in enumerate(results)
        }
        normalized_original_scores = self._min_max_normalize(original_scores)

        reranked_results: list[RetrievalResult] = []

        for index, result in enumerate(results):
            chunk_text = get_chunk_text(result)

            normalized_retriever_score = normalized_original_scores.get(index, 0.0)
            keyword_score = compute_keyword_score(query, chunk_text)

            fusion_score = (
                self.retriever_weight * normalized_retriever_score
                + (1.0 - self.retriever_weight) * keyword_score
            )

            metadata = dict(result.metadata)
            metadata["original_score"] = float(result.score)
            metadata["normalized_retriever_score"] = float(normalized_retriever_score)
            metadata["keyword_rerank_score"] = float(keyword_score)
            metadata["fusion_score"] = float(fusion_score)
            metadata["retriever_weight"] = self.retriever_weight
            metadata["rank_before_rerank"] = result.metadata.get("rank")
            metadata["reranker"] = "score_fusion"

            reranked_results.append(
                RetrievalResult(
                    chunk=result.chunk,
                    score=float(fusion_score),
                    source=f"{result.source}+score_fusion_rerank" if result.source else "score_fusion_rerank",
                    metadata=metadata,
                )
            )

        reranked_results.sort(key=lambda item: item.score, reverse=True)

        for rank, result in enumerate(reranked_results, start=1):
            result.metadata["rank"] = rank

        return reranked_results[:top_k]

    @staticmethod
    def _min_max_normalize(scores: dict[int, float]) -> dict[int, float]:
        if not scores:
            return {}

        values = list(scores.values())
        min_score = min(values)
        max_score = max(values)

        if max_score == min_score:
            return {
                key: 1.0
                for key in scores
            }

        return {
            key: (value - min_score) / (max_score - min_score)
            for key, value in scores.items()
        }