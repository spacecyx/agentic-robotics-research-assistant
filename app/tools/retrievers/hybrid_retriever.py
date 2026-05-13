# 混合检索 | 既能听懂你的字面意思(TF-IDF)，也能理解你的言外之意(Embedding)
from typing import Any

from app.tools.retrievers.embedding_retriever import EmbeddingRetriever
from app.tools.retrievers.schemas import RetrievalResult
from app.tools.retrievers.tfidf_retriever import TfidfRetriever

class HybridRetriever:
    """
    Hybrid Retriever = TF-IDF keyword retrieval + Embedding semantic retrieval.

    目标：
    1. TF-IDF 负责精确关键词召回
    2. Embedding 负责语义相似召回
    3. Hybrid 负责融合两路召回结果并重新排序
    """

    def __init__(
        self,
        chunks: list[Any],
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        alpha: float = 0.6,
        candidate_k: int = 20,
    ):
        if not chunks:
            raise ValueError("HybridRetriever requires a non-empty chunk list.")

        if not 0.0 <= alpha <= 1.0:
            raise ValueError("alpha must be between 0.0 and 1.0.")

        self.chunks = chunks
        self.alpha = alpha
        self.candidate_k = max(1, min(candidate_k, len(chunks)))

        # 双路召回
        # TF-IDF 检索 | 专业术语或产品型号
        self.tfidf_retriever = TfidfRetriever(chunks=chunks)
        # Embedding 检索 | 意思相近
        self.embedding_retriever = EmbeddingRetriever(
            chunks=chunks,
            model_name=model_name,
        )

    def search(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        if not query.strip():
            raise ValueError("Query must not be empty.")

        top_k = max(1, min(top_k, len(self.chunks)))
        candidate_k = max(top_k, min(self.candidate_k, len(self.chunks)))

        # 并发/先后检索 | 分别从 TF-IDF 和 Embedding 检索器中拿回前 candidate_k 个候选结果
        tfidf_results = self.tfidf_retriever.search(query=query, top_k=candidate_k)
        embedding_results = self.embedding_retriever.search(query=query, top_k=candidate_k)

        # 用 Python 的 id(chunk) 作为唯一标识
        tfidf_scores = {
            id(result.chunk): result.score
            for result in tfidf_results
        }
        embedding_scores = {
            id(result.chunk): result.score
            for result in embedding_results
        }

        # 把两个渠道的结果汇总到一起
        chunk_map = {}
        for result in tfidf_results + embedding_results:
            chunk_map[id(result.chunk)] = result.chunk

        # min-max 归一化 | 将两路检索出来的原始分数缩放至 0~1 具备可比性
        normalized_tfidf_scores = self._min_max_normalize(tfidf_scores)
        normalized_embedding_scores = self._min_max_normalize(embedding_scores)

        hybrid_results: list[RetrievalResult] = []

        for chunk_id, chunk in chunk_map.items():
            # default score = 0.0
            tfidf_score = tfidf_scores.get(chunk_id, 0.0)
            embedding_score = embedding_scores.get(chunk_id, 0.0)

            normalized_tfidf_score = normalized_tfidf_scores.get(chunk_id, 0.0)
            normalized_embedding_score = normalized_embedding_scores.get(chunk_id, 0.0)

            # 混合检索的 α 参数权重控制
            # 计算混合分 | Score = α × EmbeddingScore + (1 - α) × TfidfScore | 看重语义
            hybrid_score = (
                self.alpha * normalized_embedding_score
                + (1.0 - self.alpha) * normalized_tfidf_score
            )

            hybrid_results.append(
                RetrievalResult(
                    chunk=chunk,
                    score=float(hybrid_score),
                    source="hybrid",
                    metadata={
                        "tfidf_score": float(tfidf_score),
                        "embedding_score": float(embedding_score),
                        "normalized_tfidf_score": float(normalized_tfidf_score),
                        "normalized_embedding_score": float(normalized_embedding_score),
                        "alpha": self.alpha,
                    },
                )
            )

        # 按照混合后的得分从高到低排序
        hybrid_results.sort(key=lambda item: item.score, reverse=True)

        # 排序后 result 添加 rank 属性
        for rank, result in enumerate(hybrid_results, start=1):
            result.metadata["rank"] = rank

        return hybrid_results[:top_k]

    # min-max 归一化
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