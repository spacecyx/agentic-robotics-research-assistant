# 报告生成节点
# 该节点不调用模型
# 负责把 LangGraph 各节点产物整理成最终 Markdown 报告

from typing import Any

from app.states import PaperState
from app.tools.report_writer import build_report_output_path, save_markdown_report
from app.tools.trace_writer import save_trace


def format_retrieval_pipeline_config(state: PaperState) -> str:
    """
    格式化 RAG pipeline 配置。
    """

    retriever_type = state.get("retriever_type", "tfidf")
    embedding_model = state.get("embedding_model", "")
    top_k = state.get("top_k", 5)

    retriever_candidate_k = state.get("retriever_candidate_k", "")
    reranker_type = state.get("reranker_type", "none")
    reranker_top_k = state.get("reranker_top_k", "")
    retriever_weight = state.get("retriever_weight", "")
    hybrid_alpha = state.get("hybrid_alpha", "")

    max_context_chars = state.get("max_context_chars", "")
    max_chunk_chars = state.get("max_chunk_chars", "")

    faiss_index_dir = state.get("faiss_index_dir", "")
    rebuild_faiss_index = state.get("rebuild_faiss_index", False)

    use_query_expansion = state.get("use_query_expansion", False)
    query_expansion_max_queries = state.get("query_expansion_max_queries", "")
    multi_query_per_query_k = state.get("multi_query_per_query_k", "")
    multi_query_rrf_k = state.get("multi_query_rrf_k", "")

    return f"""- Retriever Type: {retriever_type}
- Embedding Model: {embedding_model}
- Final Top-K: {top_k}
- Retriever Candidate K: {retriever_candidate_k}
- Reranker Type: {reranker_type}
- Reranker Top-K: {reranker_top_k}
- Retriever Weight: {retriever_weight}
- Hybrid Alpha: {hybrid_alpha}
- Max Context Chars: {max_context_chars}
- Max Chunk Chars: {max_chunk_chars}
- FAISS Index Dir: {faiss_index_dir}
- Rebuild FAISS Index: {rebuild_faiss_index}
- Use Query Expansion: {use_query_expansion}
- Query Expansion Max Queries: {query_expansion_max_queries}
- Multi-query Per-query K: {multi_query_per_query_k}
- Multi-query RRF K: {multi_query_rrf_k}"""


def format_expanded_queries(state: PaperState) -> str:
    """
    格式化 Query Expansion 生成的 query variants。
    """

    expanded_queries = state.get("expanded_queries", [])

    if not expanded_queries:
        return "No query expansion used."

    lines = []

    for index, query in enumerate(expanded_queries, start=1):
        lines.append(f"{index}. {query}")

    return "\n".join(lines)


def format_list_preview(values: Any, max_items: int = 5) -> str:
    """
    安全展示 metadata 中的 list 字段，避免报告过长。
    """

    if not values:
        return "N/A"

    if not isinstance(values, list):
        return str(values)

    preview = values[:max_items]

    suffix = ""
    if len(values) > max_items:
        suffix = f" ... ({len(values)} total)"

    return f"{preview}{suffix}"


def format_retrieved_evidence_details(
    retrieval_results: list[Any],
    max_chars_per_chunk: int = 1200,
) -> str:
    """
    详细展示最终进入报告的检索结果。

    retrieval_results 应该是经过：
    1. first-stage retrieval
    2. optional query expansion / multi-query retrieval
    3. optional reranking

    之后的 final_results。
    """

    if not retrieval_results:
        return "No retrieved evidence available."

    evidence_blocks = []

    for rank, retrieval_result in enumerate(retrieval_results, start=1):
        chunk = retrieval_result.chunk
        score = retrieval_result.score
        source = getattr(retrieval_result, "source", "")
        metadata = getattr(retrieval_result, "metadata", {}) or {}
        page_start = getattr(chunk, "page_start", None)
        page_end = getattr(chunk, "page_end", None)
        section_title = getattr(chunk, "section_title", None)

        text = chunk.text.strip()

        if len(text) > max_chars_per_chunk:
            text = text[:max_chars_per_chunk].rstrip() + "\n..."

        # Reranker metadata
        rank_before_rerank = metadata.get("rank_before_rerank", "N/A")
        original_score = metadata.get("original_score", "N/A")
        keyword_rerank_score = metadata.get("keyword_rerank_score", "N/A")
        fusion_score = metadata.get("fusion_score", "N/A")
        normalized_retriever_score = metadata.get("normalized_retriever_score", "N/A")
        reranker = metadata.get("reranker", "N/A")

        # FAISS / embedding metadata
        faiss_score = metadata.get("faiss_score", "N/A")
        embedding_score = metadata.get("embedding_score", "N/A")
        index_dir = metadata.get("index_dir", "N/A")

        # Multi-query metadata
        multi_query = metadata.get("multi_query", False)
        matched_query_count = metadata.get("matched_query_count", "N/A")
        matched_queries = metadata.get("matched_queries", [])
        original_ranks = metadata.get("original_ranks", [])
        original_scores = metadata.get("original_scores", [])
        best_original_rank = metadata.get("best_original_rank", "N/A")
        best_original_score = metadata.get("best_original_score", "N/A")

        block = f"""### Rank {rank}

- Chunk ID: {chunk.chunk_id}
- Final Score: {score:.4f}
- Source: {source}
- Page Range: {page_start} - {page_end}
- Section: {section_title or "Unknown"}
- Char Range: {chunk.start_char} - {chunk.end_char}

Retrieval / Rerank Metadata:

- Reranker: {reranker}
- Rank Before Rerank: {rank_before_rerank}
- Original Retriever Score: {original_score}
- Normalized Retriever Score: {normalized_retriever_score}
- Keyword Rerank Score: {keyword_rerank_score}
- Fusion Score: {fusion_score}

FAISS / Embedding Metadata:

- FAISS Score: {faiss_score}
- Embedding Score: {embedding_score}
- FAISS Index Dir: {index_dir}

Multi-query Metadata:

- Multi-query: {multi_query}
- Matched Query Count: {matched_query_count}
- Best Original Rank: {best_original_rank}
- Best Original Score: {best_original_score}
- Original Ranks: {format_list_preview(original_ranks)}
- Original Scores: {format_list_preview(original_scores)}
- Matched Queries: {format_list_preview(matched_queries)}

Excerpt:

```text
{text}
```"""

        evidence_blocks.append(block)

    return "\n\n".join(evidence_blocks)


def format_generation_warnings(state: PaperState) -> str:
    """
    Format LLM invocation warnings only when fallback output was used.
    """

    llm_invocations = state.get("llm_invocations", [])
    failed_invocations = [
        invocation
        for invocation in llm_invocations
        if invocation.get("fallback_used") or not invocation.get("ok", True)
    ]

    if not failed_invocations:
        return ""

    lines = [
        "## Generation Warnings",
        "",
        "Some LLM generation steps failed and fallback text was used so the report could still be generated.",
        "",
    ]

    for invocation in failed_invocations:
        lines.append(
            "- "
            f"Node: {invocation.get('node_name', 'unknown')}; "
            f"Error Type: {invocation.get('error_type', 'unknown_error')}; "
            f"Attempts: {invocation.get('attempts', 'N/A')}; "
            f"Latency(ms): {invocation.get('latency_ms', 0.0):.2f}; "
            f"Timeout(s): {invocation.get('timeout_seconds', 'N/A')}; "
            f"Max Retries: {invocation.get('max_retries', 'N/A')}"
        )

    return "\n".join(lines)


def format_conditional_branch_warnings(state: PaperState) -> str:
    """
    Format retrieval quality branch warnings.
    """

    if not state.get("enable_conditional_branch", False):
        return ""

    decision = state.get("conditional_branch_decision", "")
    fallback_reason = state.get("fallback_reason", "")
    retry_count = state.get("retrieval_retry_count", 0) or 0
    retrieval_quality = state.get("retrieval_quality", {}) or {}

    if retry_count <= 0 and decision not in {"proceed_with_warning", "fallback"}:
        return ""

    reasons = retrieval_quality.get("reasons", [])
    quality_label = retrieval_quality.get("quality_label", "unknown")

    lines = [
        "## Retrieval Quality Warnings",
        "",
    ]

    if retry_count > 0:
        lines.append(f"- Query expansion retry was triggered {retry_count} time(s).")

    if decision == "fallback":
        lines.append("- Retrieved context was empty, so fallback text was used instead of LLM generation.")
    elif decision == "proceed_with_warning":
        lines.append("- Retrieved evidence remained weak after retry; the report was generated with a warning.")

    lines.append(f"- Final retrieval quality: {quality_label}.")

    if fallback_reason:
        lines.append(f"- Reason: {fallback_reason}.")
    elif reasons:
        lines.append("- Reason: " + ", ".join(reasons[:3]) + ".")

    return "\n".join(lines)


def generate_report_node(state: PaperState) -> PaperState:
    print(">>> running generate_report_node")

    pdf_path = state.get("pdf_path", "")
    query = state.get("query", "")

    paper_title = state.get("paper_title", "Unknown Paper")
    paper_summary = state.get("paper_summary", "")
    paper_critique = state.get("paper_critique", "")

    retrieval_results = state.get("retrieval_results", [])
    retrieved_context = state.get("retrieved_context", "")
    retrieval_evidence = state.get("retrieval_evidence", "")

    pipeline_config = format_retrieval_pipeline_config(state)
    expanded_queries = format_expanded_queries(state)

    retrieved_evidence_details = format_retrieved_evidence_details(
        retrieval_results=retrieval_results,
    )
    conditional_branch_warnings = format_conditional_branch_warnings(state)
    generation_warnings = format_generation_warnings(state)

    if not retrieval_evidence:
        retrieval_evidence = "No structured retrieval evidence available. Please check retrieve_context_node."

    final_report = f"""# Paper Analysis Report

## Input

- PDF: `{pdf_path}`
- Query: {query}

## Paper Title

{paper_title}

## Retrieval Pipeline

{pipeline_config}

## Expanded Queries

{expanded_queries}

## Retrieved Evidence Metadata

{retrieval_evidence}

## Retrieved Evidence Details

{retrieved_evidence_details}

## Retrieved Context Passed to LLM

```text
{retrieved_context}
```

## Paper Summary

{paper_summary}

## Technical Critique

{paper_critique}

{conditional_branch_warnings}

{generation_warnings}

## Final Notes

This report was generated by a LangGraph-based RAG pipeline.

The current pipeline includes:

```text
PDF loading
  -> text splitting
  -> candidate retrieval
  -> optional FAISS vector retrieval
  -> optional query expansion / multi-query retrieval
  -> optional reranking
  -> context construction
  -> evidence-aware report generation
```

The analysis is grounded in the retrieved paper chunks listed above.
"""

    output_path = build_report_output_path(pdf_path)
    save_markdown_report(final_report, output_path)

    trace_path = ""
    trace_state: PaperState = {
        **state,
        "final_report": final_report,
        "output_path": output_path,
    }

    if not state.get("disable_trace", False):
        trace_path = save_trace(
            state=trace_state,
            trace_dir=state.get("trace_dir", "outputs/traces"),
        )

    return {
        "final_report": final_report,
        "output_path": output_path,
        "trace_path": trace_path,
    }
