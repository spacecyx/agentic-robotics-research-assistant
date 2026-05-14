# 测试完整 RAG QA 链路
# 运行方式：
# python scripts/test_answer_generator.py

from app.tools.text_splitter import TextChunk
from app.tools.retrievers.factory import create_retriever
from app.tools.rerankers.factory import create_reranker
from app.tools.context_builder import ContextBuilder
from app.tools.answer_generator import AnswerGenerator


def main() -> None:
    chunks = [
        TextChunk(
            chunk_id=0,
            text=(
                "ResNet introduces residual learning to address the degradation problem. "
                "Shortcut connections make it easier to learn identity mappings. "
                "Instead of directly learning the desired underlying mapping H(x), "
                "the residual block learns F(x) = H(x) - x and outputs F(x) + x."
            ),
            start_char=0,
            end_char=260,
        ),
        TextChunk(
            chunk_id=1,
            text=(
                "The Transformer uses self-attention instead of recurrence or convolution. "
                "Multi-head attention allows the model to jointly attend to information "
                "from different representation subspaces at different positions."
            ),
            start_char=261,
            end_char=470,
        ),
        TextChunk(
            chunk_id=2,
            text=(
                "TF-IDF retrieval is based on lexical matching. "
                "It works well when the query and document share exact keywords."
            ),
            start_char=471,
            end_char=590,
        ),
        TextChunk(
            chunk_id=3,
            text=(
                "Embedding retrieval maps text into vector space and searches by semantic similarity."
            ),
            start_char=591,
            end_char=680,
        ),
        TextChunk(
            chunk_id=4,
            text=(
                "Reranking is often used as a second-stage retrieval method. "
                "The first stage recalls candidates and the second stage improves ranking precision."
            ),
            start_char=681,
            end_char=840,
        ),
    ]

    query = "为什么 ResNet 要使用 shortcut connection，它解决了什么训练问题？"

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
        max_context_chars=1500,
        max_chunk_chars=600,
    )

    built_context = context_builder.build(
        results=reranked_results,
        max_results=3,
    )

    evidence_markdown = context_builder.build_evidence_markdown(
        built_context.evidences,
    )

    answer_generator = AnswerGenerator(
        paper_title="Deep Residual Learning for Image Recognition",
    )

    answer_result = answer_generator.generate(
        query=query,
        context=built_context.context,
        evidence_markdown=evidence_markdown,
    )

    print("\n" + "=" * 80)
    print("Built Context")
    print("=" * 80)
    print(built_context.context)

    print("\n" + "=" * 80)
    print("Generated Answer")
    print("=" * 80)
    print(answer_result.final_markdown)


if __name__ == "__main__":
    main()