from app.states import PaperState
from app.tools.retrievers.factory import create_retriever
from app.tools.rerankers.factory import create_reranker
from app.tools.context_builder import ContextBuilder


def retrieve_context_node(state: PaperState) -> PaperState:
    print(">>> running retrieve_context_node")

    query = state["query"]
    chunks = state["chunks"]

    # 最终进入 LLM 的 chunk 数量
    top_k = state.get("top_k", 5)

    # 第一阶段召回候选数量，通常应该大于最终 top_k
    retriever_candidate_k = state.get("retriever_candidate_k", max(top_k * 3, 10))

    retriever_type = state.get("retriever_type", "tfidf")
    embedding_model = state.get(
        "embedding_model",
        "sentence-transformers/all-MiniLM-L6-v2",
    )

    # Hybrid retriever 参数
    hybrid_alpha = state.get("hybrid_alpha", 0.6)

    # Reranker 参数
    reranker_type = state.get("reranker_type", "score_fusion")
    reranker_top_k = state.get("reranker_top_k", top_k)
    retriever_weight = state.get("retriever_weight", 0.7)

    # ContextBuilder 参数
    max_context_chars = state.get("max_context_chars", 4000)
    max_chunk_chars = state.get("max_chunk_chars", 1200)

    # 1. 第一阶段召回
    retriever = create_retriever(
        retriever_type=retriever_type,
        chunks=chunks,
        embedding_model=embedding_model,
        alpha=hybrid_alpha,
        candidate_k=retriever_candidate_k,
    )

    retrieved_results = retriever.search(
        query=query,
        top_k=retriever_candidate_k,
    )

    # 2. 第二阶段重排
    if reranker_type and reranker_type.lower().strip() not in {"none", "no", "disable"}:
        reranker = create_reranker(
            reranker_type=reranker_type,
            retriever_weight=retriever_weight,
        )

        final_results = reranker.rerank(
            query=query,
            results=retrieved_results,
            top_k=reranker_top_k,
        )
    else:
        final_results = retrieved_results[:top_k]

    # 3. 构造 LLM 上下文
    context_builder = ContextBuilder(
        max_context_chars=max_context_chars,
        max_chunk_chars=max_chunk_chars,
    )

    built_context = context_builder.build(
        results=final_results,
        max_results=top_k,
    )

    retrieval_evidence = context_builder.build_evidence_markdown(
        built_context.evidences,
    )

    return {
        "retriever_type": retriever_type,
        "embedding_model": embedding_model,
        "retriever_candidate_k": retriever_candidate_k,
        "reranker_type": reranker_type,
        "reranker_top_k": reranker_top_k,
        "retriever_weight": retriever_weight,
        "retrieval_results": final_results,
        "retrieved_context": built_context.context,
        "retrieval_evidence": retrieval_evidence,
    }