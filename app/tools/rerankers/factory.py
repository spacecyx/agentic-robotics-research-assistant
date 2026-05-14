# Reranker Factory
# 作用：统一创建不同类型的 reranker | 可拓展

from app.tools.rerankers.base import BaseReranker
from app.tools.rerankers.keyword_reranker import KeywordReranker
from app.tools.rerankers.score_fusion_reranker import ScoreFusionReranker


def create_reranker(
    reranker_type: str,
    retriever_weight: float = 0.7,
) -> BaseReranker:
    """
    创建 Reranker。

    支持：
    1. keyword
    2. score_fusion / fusion
    """

    reranker_type = reranker_type.lower().strip()

    if reranker_type == "keyword":
        return KeywordReranker()

    if reranker_type in {"score_fusion", "fusion"}:
        return ScoreFusionReranker(
            retriever_weight=retriever_weight,
        )

    raise ValueError(
        f"Unsupported reranker_type: {reranker_type}. "
        "Supported types: keyword, score_fusion."
    )