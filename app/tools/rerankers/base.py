# 给所有 reranker 一个统一接口 | 让 Reranker 和 Retriever 一样，也有统一协议
from typing import Protocol

from app.tools.retrievers.schemas import RetrievalResult


class BaseReranker(Protocol):
    """
    Reranker 统一接口。

    输入：
        query: 用户问题
        results: Retriever 返回的候选结果
        top_k: 重排后保留的结果数量

    输出：
        重排后的 RetrievalResult 列表
    """

    def rerank(
        self,
        query: str,
        results: list[RetrievalResult],
        top_k: int = 5,
    ) -> list[RetrievalResult]:
        ...


def get_chunk_text(result: RetrievalResult) -> str:
    """
    从 RetrievalResult 中提取 chunk 文本。

    当前项目中的 chunk 是 TextChunk，文本字段为 chunk.text。
    这里单独封装一层，是为了以后兼容其他 chunk 格式。
    """

    chunk = result.chunk

    if hasattr(chunk, "text"):
        return str(chunk.text)

    return str(chunk)