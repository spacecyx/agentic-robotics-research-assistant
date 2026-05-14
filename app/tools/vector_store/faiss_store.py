# FAISS 本地向量索引存储模块
# 负责 build / save / load / search

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer

from app.tools.text_splitter import TextChunk


def import_faiss():
    try:
        import faiss
    except ImportError as exc:
        raise ImportError(
            "faiss is not installed. Please run: pip install faiss-cpu"
        ) from exc

    return faiss


def chunk_to_dict(chunk: TextChunk) -> dict[str, Any]:
    return {
        "chunk_id": chunk.chunk_id,
        "text": chunk.text,
        "start_char": chunk.start_char,
        "end_char": chunk.end_char,
    }


def dict_to_chunk(data: dict[str, Any]) -> TextChunk:
    return TextChunk(
        chunk_id=int(data["chunk_id"]),
        text=str(data["text"]),
        start_char=int(data["start_char"]),
        end_char=int(data["end_char"]),
    )


def compute_chunks_fingerprint(chunks: list[TextChunk]) -> str:
    """
    根据 chunks 内容计算指纹，避免错误加载其他 PDF 的索引。
    """

    hasher = hashlib.md5()

    for chunk in chunks:
        item = {
            "chunk_id": chunk.chunk_id,
            "text": chunk.text,
            "start_char": chunk.start_char,
            "end_char": chunk.end_char,
        }
        hasher.update(
            json.dumps(item, ensure_ascii=False, sort_keys=True).encode("utf-8")
        )

    return hasher.hexdigest()


class FaissVectorStore:
    """
    FAISS Vector Store。

    使用 normalized embeddings + IndexFlatIP。
    因为 embedding 已归一化，所以 inner product 等价于 cosine similarity。
    """

    INDEX_FILE = "faiss.index"              # 向量索引 | "地图" 用来快速定位答案大概在哪
    CHUNKS_FILE = "chunks.json"             # 原始文本块 | 找到"地图"位置后，取出的实际文字内容
    EMBEDDINGS_FILE = "embeddings.npy"      # 向量矩阵 | 存储计算好的原始数字特征
    META_FILE = "index_meta.json"           # 元数据 | 记录用了什么模型、向量维度是多少等配置信息

    def __init__(
        self,
        chunks: list[TextChunk],
        embeddings: np.ndarray,
        model_name: str,
        index,
        metadata: dict[str, Any],
        model: SentenceTransformer,
    ):
        self.chunks = chunks
        self.embeddings = embeddings
        self.model_name = model_name
        self.index = index
        self.metadata = metadata
        self.model = model

    @classmethod
    def build(
        cls,
        chunks: list[TextChunk],
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> "FaissVectorStore":
        if not chunks:
            raise ValueError("FaissVectorStore requires a non-empty chunk list.")

        faiss = import_faiss()

        texts = [chunk.text for chunk in chunks]

        model = SentenceTransformer(
            model_name,
            local_files_only=True,
        )

        embeddings = model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=True,
        )

        embeddings = np.asarray(embeddings, dtype=np.float32)

        embedding_dim = embeddings.shape[1]

        index = faiss.IndexFlatIP(embedding_dim)
        index.add(embeddings)

        metadata = {
            "model_name": model_name,
            "num_chunks": len(chunks),
            "embedding_dim": int(embedding_dim),
            "index_type": "IndexFlatIP",
            "normalize_embeddings": True,
            "chunks_fingerprint": compute_chunks_fingerprint(chunks),
        }

        return cls(
            chunks=chunks,
            embeddings=embeddings,
            model_name=model_name,
            index=index,
            metadata=metadata,
            model=model,
        )

    def save(self, index_dir: str | Path) -> None:
        index_dir = Path(index_dir)
        index_dir.mkdir(parents=True, exist_ok=True)

        faiss = import_faiss()

        faiss.write_index(
            self.index,
            str(index_dir / self.INDEX_FILE),
        )

        np.save(
            index_dir / self.EMBEDDINGS_FILE,
            self.embeddings,
        )

        with (index_dir / self.CHUNKS_FILE).open("w", encoding="utf-8") as f:
            json.dump(
                [chunk_to_dict(chunk) for chunk in self.chunks],
                f,
                ensure_ascii=False,
                indent=2,
            )

        with (index_dir / self.META_FILE).open("w", encoding="utf-8") as f:
            json.dump(
                self.metadata,
                f,
                ensure_ascii=False,
                indent=2,
            )

    @classmethod
    def load(cls, index_dir: str | Path) -> "FaissVectorStore":
        index_dir = Path(index_dir)

        index_path = index_dir / cls.INDEX_FILE
        chunks_path = index_dir / cls.CHUNKS_FILE
        embeddings_path = index_dir / cls.EMBEDDINGS_FILE
        meta_path = index_dir / cls.META_FILE

        for path in [index_path, chunks_path, embeddings_path, meta_path]:
            if not path.exists():
                raise FileNotFoundError(f"Missing FAISS index file: {path}")

        faiss = import_faiss()

        index = faiss.read_index(str(index_path))
        embeddings = np.load(embeddings_path)

        with chunks_path.open("r", encoding="utf-8") as f:
            chunks_data = json.load(f)

        chunks = [
            dict_to_chunk(item)
            for item in chunks_data
        ]

        with meta_path.open("r", encoding="utf-8") as f:
            metadata = json.load(f)

        model_name = metadata["model_name"]

        model = SentenceTransformer(
            model_name,
            local_files_only=True,
        )

        return cls(
            chunks=chunks,
            embeddings=embeddings,
            model_name=model_name,
            index=index,
            metadata=metadata,
            model=model,
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[tuple[int, float, TextChunk]]:
        if not query.strip():
            raise ValueError("Query must not be empty.")

        top_k = max(1, min(top_k, len(self.chunks)))

        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        query_embedding = np.asarray(query_embedding, dtype=np.float32)

        scores, indices = self.index.search(
            query_embedding,
            top_k,
        )

        results: list[tuple[int, float, TextChunk]] = []

        for index, score in zip(indices[0], scores[0]):
            if index < 0:
                continue

            chunk = self.chunks[int(index)]
            results.append(
                (
                    int(index),
                    float(score),
                    chunk,
                )
            )

        return results