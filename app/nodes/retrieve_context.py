from app.states import PaperState
from app.tools.retrievers.factory import create_retriever
from app.tools.rerankers.factory import create_reranker
from app.tools.context_builder import ContextBuilder
from app.tools.retrievers.multi_query_retriever import MultiQueryRetriever
from app.tools.query_expansion import HeuristicQueryExpander


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

    # FAISS retriever 参数 (plus)
    faiss_index_dir = state.get("faiss_index_dir", "")
    rebuild_faiss_index = state.get("rebuild_faiss_index", False)

    # Query Expansion 参数
    use_query_expansion = state.get("use_query_expansion", False)
    query_expansion_max_queries = state.get("query_expansion_max_queries", 4)
    multi_query_per_query_k = state.get("multi_query_per_query_k", retriever_candidate_k)
    multi_query_rrf_k = state.get("multi_query_rrf_k", 60)

    # Reranker 参数
    reranker_type = state.get("reranker_type", "score_fusion")
    reranker_top_k = state.get("reranker_top_k", top_k)
    retriever_weight = state.get("retriever_weight", 0.7)

    # ContextBuilder 参数
    max_context_chars = state.get("max_context_chars", 4000)
    max_chunk_chars = state.get("max_chunk_chars", 1200)

    # 1. 创建基础 retriever
    base_retriever = create_retriever(
        retriever_type=retriever_type,
        chunks=chunks,
        embedding_model=embedding_model,
        alpha=hybrid_alpha,
        candidate_k=retriever_candidate_k,
        faiss_index_dir=faiss_index_dir or None,
        rebuild_faiss_index=rebuild_faiss_index,
    )

    # 2. 可选：Query Expansion + Multi-query retrieval
    expanded_queries = [query]

    if use_query_expansion:
        query_expander = HeuristicQueryExpander()

        retriever = MultiQueryRetriever(
            base_retriever=base_retriever,
            query_expander=query_expander,
            max_queries=query_expansion_max_queries,
            per_query_k=multi_query_per_query_k,
            rrf_k=multi_query_rrf_k,
        )

        retrieved_results = retriever.search(
            query=query,
            top_k=retriever_candidate_k,
        )

        expanded_queries = retriever.last_expanded_queries
    else:
        retriever = base_retriever

        retrieved_results = retriever.search(
            query=query,
            top_k=retriever_candidate_k,
        )

    # 3. 第二阶段重排
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

    # 4. 构造 LLM 上下文
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
        "faiss_index_dir": faiss_index_dir,
        "rebuild_faiss_index": rebuild_faiss_index,
        "use_query_expansion": use_query_expansion,
        "query_expansion_max_queries": query_expansion_max_queries,
        "multi_query_per_query_k": multi_query_per_query_k,
        "multi_query_rrf_k": multi_query_rrf_k,
        "expanded_queries": expanded_queries,
    }