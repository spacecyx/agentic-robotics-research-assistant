from typing import Any, TypedDict

# Day 4 import
# from app.tools.text_splitter import TextChunk
# from app.tools.retrievers.schemas import RetrievalResult
# 注释原因：先用 Any, 即不导入 Chunk、RetrievalResult 等强类型
#          现在项目还在快速迭代阶段，过早强类型可能引入循环导入问题

# 定义 Agent 工作流里所有节点共享的数据结构
# total=False:LangGraph 每个节点只返回自己更新的字段，不需要每个节点都补全所有字段
class PaperState(TypedDict, total=False):
    """
    State shared across the paper analysis workflow 
    LangGraph 中所有节点共享和更新的状态对象
    """

    # User inputs
    pdf_path: str
    query: str
    top_k: int
    retriever_type: str         # new add in Day 6 
    embedding_model: str        # new add in Day 6 

    # PDF parsing
    raw_text: str
    paper_text: str
    paper_title: str

    # Text splitting
    chunks: list[Any]
    # chunks: list[TextChunk]

    # FAISS
    faiss_index_dir: str
    rebuild_faiss_index: bool
    
    # Retrieval
    hybrid_alpha: float
    retrieval_results: list[Any]
    retrieved_context: str
    max_context_chars: int
    max_chunk_chars: int

    # Query Expansion / Multi-query retrieval
    use_query_expansion: bool
    query_expansion_max_queries: int
    multi_query_per_query_k: int
    multi_query_rrf_k: int
    expanded_queries: list[str]

    # Reranking / Context building 
    reranker_type: str              # keyword / score_fusion / section_prior / none
    reranker_top_k: int             # 重排后保留多少 chunk
    retriever_candidate_k: int      # 第一阶段召回多少候选 chunk
    retriever_weight: float         # ScoreFusionReranker 中原始检索分数的权重
    retrieval_evidence: str         # ContextBuilder 生成的 evidence markdown

    # LLM outputs/analysis
    paper_summary: str
    paper_critique: str
    errors: list[dict[str, Any]]
    llm_invocations: list[dict[str, Any]]

    # Final report
    final_report: str
    output_path: str

    # Trace logging
    trace_dir: str
    disable_trace: bool
    trace_path: str
