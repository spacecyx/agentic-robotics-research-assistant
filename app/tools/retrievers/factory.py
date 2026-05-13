# 后续增加 BM25、Hybrid、Reranker 时，只需要扩展这个 factory
# 作用:实现软件设计模式中的工厂模式 | 屏蔽复杂度（封装）;即插即用
from typing import Any

from app.tools.retrievers.base import BaseRetriever
from app.tools.retrievers.tfidf_retriever import TfidfRetriever
from app.tools.retrievers.embedding_retriever import EmbeddingRetriever
from app.tools.retrievers.hybrid_retriever import HybridRetriever


def create_retriever(
    retriever_type: str,
    chunks: list[Any],
    embedding_model: str | None = None,
    alpha: float = 0.6,
    candidate_k: int = 20,
) -> BaseRetriever:
    # 归一化处理 | 大小写保护
    retriever_type = retriever_type.lower().strip()

    if retriever_type == "tfidf":
        return TfidfRetriever(chunks=chunks)

    if retriever_type == "embedding":
        return EmbeddingRetriever(
            chunks=chunks,
            # 默认配置控制 default_model:all-MiniLM-L6-v2
            model_name=embedding_model or "sentence-transformers/all-MiniLM-L6-v2",
        )
    
    # new add hybrid retriever in Day 7
    if retriever_type == "hybrid":
        return HybridRetriever(
            chunks=chunks,
            model_name=embedding_model or "sentence-transformers/all-MiniLM-L6-v2",
            alpha=alpha,
            candidate_k=candidate_k,
        )

    # RAG 检索方法输入鲁棒 意外方法直接抛错
    raise ValueError(
        f"Unsupported retriever_type: {retriever_type}. "
        "Supported types: tfidf, embedding, hybrid."
    )

# factory 在 RAG 管道中的位置:
# 1. 用户上传文档 -> 2. 切片 (Chunks) -> 3. 工厂 (Factory) 生成检索器 -> 4. 检索器创建索引 -> 5. 开始问答

