# FAISS Retriever
# 使用本地持久化向量索引进行 embedding 检索

from pathlib import Path
from typing import Any

from app.tools.retrievers.schemas import RetrievalResult
from app.tools.vector_store.faiss_store import (
    FaissVectorStore,
    compute_chunks_fingerprint,
)


class FaissRetriever:
    """
    基于 FAISS 的本地向量检索器。

    和 EmbeddingRetriever 保持同一套输出协议：
    search(query, top_k) -> list[RetrievalResult]
    """

    def __init__(
        self,
        chunks: list[Any],
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        index_dir: str | None = None,
        rebuild_index: bool = False,
    ):
        if not chunks:
            raise ValueError("FaissRetriever requires a non-empty chunk list.")

        self.model_name = model_name
        self.index_dir = index_dir

        if index_dir:
            index_path = Path(index_dir) / FaissVectorStore.INDEX_FILE

            if index_path.exists() and not rebuild_index:
                self.vector_store = FaissVectorStore.load(index_dir)

                current_fingerprint = compute_chunks_fingerprint(chunks)
                cached_fingerprint = self.vector_store.metadata.get("chunks_fingerprint")

                if current_fingerprint != cached_fingerprint:
                    raise ValueError(
                        "Loaded FAISS index does not match current chunks. "
                        "Please use a different --faiss-index-dir or rebuild the index."
                    )

            else:
                self.vector_store = FaissVectorStore.build(
                    chunks=chunks,
                    model_name=model_name,
                )
                self.vector_store.save(index_dir)
        else:
            self.vector_store = FaissVectorStore.build(
                chunks=chunks,
                model_name=model_name,
            )

        self.chunks = self.vector_store.chunks

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievalResult]:
        if not query.strip():
            raise ValueError("Query must not be empty.")

        top_k = max(1, min(top_k, len(self.chunks)))

        search_results = self.vector_store.search(
            query=query,
            top_k=top_k,
        )

        retrieval_results: list[RetrievalResult] = []

        for rank, (chunk_index, score, chunk) in enumerate(search_results, start=1):
            retrieval_results.append(
                RetrievalResult(
                    chunk=chunk,
                    score=float(score),
                    source="faiss",
                    metadata={
                        "chunk_index": int(chunk_index),
                        "embedding_score": float(score),
                        "faiss_score": float(score),
                        "rank": rank,
                        "index_dir": self.index_dir,
                        "model_name": self.model_name,
                    },
                )
            )

        return retrieval_results