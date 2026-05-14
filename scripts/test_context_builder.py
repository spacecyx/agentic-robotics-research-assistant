# 测试 ContextBuilder 是否能正确构造上下文
# 运行方式：
# python scripts/test_context_builder.py

from app.tools.text_splitter import TextChunk
from app.tools.retrievers.factory import create_retriever
from app.tools.rerankers.factory import create_reranker
from app.tools.context_builder import ContextBuilder


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

    reranker = create_reranker(
        reranker_type="score_fusion",
        retriever_weight=0.7,
    )

    reranked_results = reranker.rerank(
        query=query,
        results=retrieved_results,
        top_k=3,
    )

    context_builder = ContextBuilder(
        max_context_chars=1200,
        max_chunk_chars=400,
    )

    built_context = context_builder.build(
        results=reranked_results,
        max_results=3,
    )

    print("\n" + "=" * 80)
    print("Built Context")
    print("=" * 80)
    print(built_context.context)

    print("\n" + "=" * 80)
    print("Evidence Markdown")
    print("=" * 80)
    print(
        context_builder.build_evidence_markdown(
            built_context.evidences,
        )
    )


if __name__ == "__main__":
    main()