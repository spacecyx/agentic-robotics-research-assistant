# 基于关键词重合度的 Reranker
# 作用：不重新检索，只对 Retriever 返回的候选结果重新排序
# 不依赖模型的 rerank baseline | 可用于和后续 Cross-Encoder Reranker 对比

import re

from app.tools.retrievers.schemas import RetrievalResult
from app.tools.rerankers.base import get_chunk_text


STOP_WORDS = {
    "a", "an", "the",
    "is", "are", "was", "were",
    "of", "to", "in", "on", "for", "with", "by",
    "and", "or", "as", "at", "from",
    "what", "why", "how", "does", "do", "did",
    "this", "that", "these", "those",
}


def tokenize(text: str) -> list[str]:
    """
    简单英文分词。

    当前项目主要处理英文论文，因此先用轻量正则分词
    后续如果要支持中文论文，可以替换为 jieba 或其他 tokenizer。
    """

    # 标准化(转小写) + 正则分词(提取所有字母、数字和下划线组成的连续片段 | 过滤空格/标点符号...)
    tokens = re.findall(r"[A-Za-z0-9_]+", text.lower())

    return [
        token
        for token in tokens
        # 剔除没有实际分析意义的虚词(STOP_WORDS) & 过滤掉单字母词
        if token not in STOP_WORDS and len(token) > 1
    ]


def compute_keyword_score(query: str, chunk_text: str) -> float:
    """
    计算 query 和 chunk 的关键词重合分数。

    这里不是严格语义分数，只是一个轻量 rerank baseline。
    """

    query_terms = set(tokenize(query))
    chunk_tokens = tokenize(chunk_text)

    if not query_terms or not chunk_tokens:
        return 0.0

    chunk_terms = set(chunk_tokens)
    matched_terms = query_terms & chunk_terms

    # 覆盖率：query 中有多少有效关键词出现在 chunk 中
    coverage_score = len(matched_terms) / len(query_terms)

    # 频次奖励：匹配词在 chunk 中出现越多，略微加分
    occurrence_count = sum(
        chunk_tokens.count(term)
        for term in matched_terms
    )
    occurrence_bonus = occurrence_count / max(len(chunk_tokens), 1)

    score = coverage_score + 0.2 * occurrence_bonus

    return float(min(score, 1.0))


class KeywordReranker:
    """
    Keyword Reranker。

    使用场景：
    1. 不依赖额外模型
    2. 不依赖网络
    3. 适合作为 rerank baseline
    """

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

        reranked_results: list[RetrievalResult] = []

        for result in results:
            chunk_text = get_chunk_text(result)
            keyword_score = compute_keyword_score(query, chunk_text)

            metadata = dict(result.metadata)
            metadata["original_score"] = float(result.score)
            metadata["rank_before_rerank"] = result.metadata.get("rank")
            metadata["keyword_rerank_score"] = float(keyword_score)
            metadata["reranker"] = "keyword"

            reranked_results.append(
                RetrievalResult(
                    chunk=result.chunk,
                    score=float(keyword_score),
                    source=f"{result.source}+keyword_rerank" if result.source else "keyword_rerank",
                    metadata=metadata,
                )
            )

        # 分数相同时，保留原始 retriever score 更高的结果
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