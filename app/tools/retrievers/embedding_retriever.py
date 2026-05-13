# embedding 检索
# 找意思上走得近的内容
# 下载的embedding模型所在目录:~/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2 (wsl中)
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer

from app.tools.retrievers.schemas import RetrievalResult

# BaseRetriever 协议的具体实现 ~ Embedding
class EmbeddingRetriever:
    def __init__(
        self,
        chunks: list[Any],
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",     # 默认一个轻量化模型
    ):
        # 首次运行 embedding 模型时会下载模型。如果网络环境不稳定，可能会卡住或失败。先用轻量模型：all-MiniLM-L6-v2
        # 该模型对英文论文检索足够作为 Day 6 的 baseline
        if not chunks:
            raise ValueError("EmbeddingRetriever requires a non-empty chunk list.")

        self.chunks = chunks
        self.texts = [chunk.text for chunk in chunks]

        # 模型加载
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

        # 全量编码 [最耗时] 把整个知识库 (chunks) 全部转化成了矩阵 self.chunk_embeddings
        self.chunk_embeddings = self.model.encode(
            self.texts,
            normalize_embeddings=True,      # 把所有向量的长度都缩放为 1 | 计算相似度会变得简单且快速[计算时]
            convert_to_numpy=True, 
            show_progress_bar=False,
        )

    def search(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        if not query.strip():
            raise ValueError("Query must not be empty.")

        top_k = max(1, min(top_k, len(self.chunks)))

        # 用户的 query 被转化成了一个同样维度的向量
        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )[0]

        # 点积计算相似度 | 已经完成归一化 点积结果即为余弦相似度
        scores = np.dot(self.chunk_embeddings, query_embedding)

        # argsort()[::-1] 按照分数从高到低排个序，取前 top_k 个
        top_indices = np.argsort(scores)[::-1][:top_k]

        return [
            RetrievalResult(
                chunk=self.chunks[index],
                score=float(scores[index]),
            )
            for index in top_indices
        ]