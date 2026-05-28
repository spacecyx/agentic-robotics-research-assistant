# Reranker Factory
# 作用：统一创建不同类型的 reranker | 可拓展

from app.tools.rerankers.base import BaseReranker
from app.tools.rerankers.keyword_reranker import KeywordReranker
from app.tools.rerankers.robotics_tag_prior_reranker import RoboticsTagPriorReranker
from app.tools.rerankers.score_fusion_reranker import ScoreFusionReranker
from app.tools.rerankers.section_prior_reranker import SectionPriorReranker


def create_reranker(
    reranker_type: str,
    retriever_weight: float = 0.7,
) -> BaseReranker:
    """
    创建 Reranker。

    支持：
    1. keyword
    2. score_fusion / fusion
    3. section_prior
    4. robotics_tag_prior
    """

    reranker_type = reranker_type.lower().strip()

    if reranker_type == "keyword":
        return KeywordReranker()

    if reranker_type in {"score_fusion", "fusion"}:
        return ScoreFusionReranker(
            retriever_weight=retriever_weight,
        )

    if reranker_type == "section_prior":
        return SectionPriorReranker(
            retrieval_weight=retriever_weight,
        )

    if reranker_type == "robotics_tag_prior":
        return RoboticsTagPriorReranker(
            retrieval_weight=retriever_weight,
        )

    raise ValueError(
        f"Unsupported reranker_type: {reranker_type}. "
        "Supported types: keyword, score_fusion, section_prior, robotics_tag_prior."
    )
