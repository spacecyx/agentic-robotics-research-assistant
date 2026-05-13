# 简单检索模块 (前期版本 | 后期走 app.tools.retrievers.tfidf_retriever)

# app/tools/simple_retriever.py

# 类似C中的结构体
from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.tools.text_splitter import TextChunk


@dataclass
class RetrievalResult:
    """
    A retrieval result containing a chunk and its similarity score.
    """

    chunk: TextChunk
    score: float


def retrieve_top_k(
    query: str,
    chunks: list[TextChunk],
    top_k: int = 3,
) -> list[RetrievalResult]:
    """
    Retrieve top-k relevant chunks using TF-IDF cosine similarity.

    Args:
        query: User query.
        chunks: List of TextChunk objects.
        top_k: Number of chunks to return.

    Returns:
        A list of RetrievalResult objects sorted by descending score.
    """

    if not query or not query.strip():
        raise ValueError("query must not be empty.")

    if not chunks:
        return []

    if top_k <= 0:
        raise ValueError("top_k must be positive.")

    texts = [chunk.text for chunk in chunks]

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
    )

    # 把 chunks 和 query 一起向量化
    tfidf_matrix = vectorizer.fit_transform(texts + [query])

    # 向量化后的 chunk
    chunk_vectors = tfidf_matrix[:-1]
    # 向量化后的 query
    query_vector = tfidf_matrix[-1]

    similarities = cosine_similarity(query_vector, chunk_vectors).flatten()

    ranked_indices = similarities.argsort()[::-1]

    results: list[RetrievalResult] = []

    for idx in ranked_indices[:top_k]:
        results.append(
            RetrievalResult(
                chunk=chunks[int(idx)],
                score=float(similarities[idx]),
            )
        )

    return results


def print_retrieval_results(
    results: list[RetrievalResult],
    max_chars: int = 700,
) -> None:
    """
    Print retrieval results for manual inspection.
    """

    if not results:
        print("No retrieval results.")
        return

    for rank, result in enumerate(results, start=1):
        chunk = result.chunk

        print("=" * 100)
        print(f"Rank: {rank}")
        print(f"Chunk ID: {chunk.chunk_id}")
        print(f"Score: {result.score:.4f}")
        print(f"Char Range: {chunk.start_char} - {chunk.end_char}")
        print("-" * 100)
        print(chunk.text[:max_chars])
        print()