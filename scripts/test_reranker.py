# 测试 Reranker 是否能独立工作

from app.tools.text_splitter import TextChunk
from app.tools.retrievers.factory import create_retriever
from app.tools.rerankers.factory import create_reranker


def main() -> None:
    chunks = [
        TextChunk(
            chunk_id=0,
            text=(
                "ResNet introduces residual learning to address the degradation problem. "
                "Shortcut connections make it easier to learn identity mappings."
            ),
            start_char=0,
            end_char=120,
        ),
        TextChunk(
            chunk_id=1,
            text=(
                "The Transformer uses self-attention instead of recurrence or convolution. "
                "Multi-head attention allows the model to attend to different representation subspaces."
            ),
            start_char=121,
            end_char=260,
        ),
        TextChunk(
            chunk_id=2,
            text=(
                "TF-IDF retrieval is based on lexical matching. "
                "It works well when the query and document share exact keywords."
            ),
            start_char=261,
            end_char=380,
        ),
        TextChunk(
            chunk_id=3,
            text=(
                "Embedding retrieval maps text into vector space and searches by semantic similarity."
            ),
            start_char=381,
            end_char=470,
        ),
        TextChunk(
            chunk_id=4,
            text=(
                "Reranking is often used as a second-stage retrieval method. "
                "The first stage recalls candidates and the second stage improves ranking precision."
            ),
            start_char=471,
            end_char=620,
        ),
    ]

    query = "Why does ResNet use shortcut connections and identity mapping?"

    retriever = create_retriever(
        retriever_type="tfidf",
        chunks=chunks,
    )

    retrieved_results = retriever.search(
        query=query,
        top_k=5,
    )

    print("\n" + "=" * 80)
    print("Original Retrieval Results")
    print("=" * 80)

    for result in retrieved_results:
        print(
            f"rank={result.metadata.get('rank')} | "
            f"score={result.score:.4f} | "
            f"chunk_id={result.chunk.chunk_id}"
        )
        print(result.chunk.text[:160])
        print("-" * 80)

    keyword_reranker = create_reranker(
        reranker_type="keyword",
    )

    keyword_results = keyword_reranker.rerank(
        query=query,
        results=retrieved_results,
        top_k=3,
    )

    print("\n" + "=" * 80)
    print("Keyword Reranked Results")
    print("=" * 80)

    for result in keyword_results:
        print(
            f"rank={result.metadata.get('rank')} | "
            f"score={result.score:.4f} | "
            f"chunk_id={result.chunk.chunk_id} | "
            f"before={result.metadata.get('rank_before_rerank')}"
        )
        print(result.chunk.text[:160])
        print("-" * 80)

    fusion_reranker = create_reranker(
        reranker_type="score_fusion",
        retriever_weight=0.7,
    )

    fusion_results = fusion_reranker.rerank(
        query=query,
        results=retrieved_results,
        top_k=3,
    )

    print("\n" + "=" * 80)
    print("Score Fusion Reranked Results")
    print("=" * 80)

    for result in fusion_results:
        print(
            f"rank={result.metadata.get('rank')} | "
            f"score={result.score:.4f} | "
            f"chunk_id={result.chunk.chunk_id} | "
            f"before={result.metadata.get('rank_before_rerank')} | "
            f"retriever_score={result.metadata.get('normalized_retriever_score'):.4f} | "
            f"keyword_score={result.metadata.get('keyword_rerank_score'):.4f}"
        )
        print(result.chunk.text[:160])
        print("-" * 80)


if __name__ == "__main__":
    main()