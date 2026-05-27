import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from app.states import PaperState


def safe_preview(text: str | None, max_chars: int = 200) -> str | None:
    if text is None:
        return None

    text = " ".join(str(text).split())

    if len(text) <= max_chars:
        return text

    return text[:max_chars].rstrip() + "..."


def _text_summary(text: str | None, max_chars: int = 200) -> dict[str, Any]:
    if text is None:
        return {
            "chars": 0,
            "preview": None,
        }

    return {
        "chars": len(text),
        "preview": safe_preview(text, max_chars=max_chars),
    }


def _summarize_chunks(chunks: list[Any], max_items: int = 5) -> dict[str, Any]:
    preview_items = []

    for chunk in chunks[:max_items]:
        preview_items.append(
            {
                "chunk_id": getattr(chunk, "chunk_id", None),
                "start_char": getattr(chunk, "start_char", None),
                "end_char": getattr(chunk, "end_char", None),
                "page_start": getattr(chunk, "page_start", None),
                "page_end": getattr(chunk, "page_end", None),
                "section_title": getattr(chunk, "section_title", None),
                "text_preview": safe_preview(getattr(chunk, "text", None)),
            }
        )

    return {
        "count": len(chunks),
        "preview_items": preview_items,
    }


def _summarize_retrieval_results(
    retrieval_results: list[Any],
    max_items: int = 10,
) -> dict[str, Any]:
    preview_items = []

    for rank, result in enumerate(retrieval_results[:max_items], start=1):
        chunk = getattr(result, "chunk", None)
        metadata = getattr(result, "metadata", {}) or {}

        preview_items.append(
            {
                "rank": rank,
                "chunk_id": getattr(chunk, "chunk_id", None),
                "score": getattr(result, "score", None),
                "source": getattr(result, "source", None),
                "start_char": getattr(chunk, "start_char", None),
                "end_char": getattr(chunk, "end_char", None),
                "page_start": getattr(chunk, "page_start", None),
                "page_end": getattr(chunk, "page_end", None),
                "section_title": getattr(chunk, "section_title", None),
                "text_preview": safe_preview(getattr(chunk, "text", None)),
                "metadata": {
                    "rank": metadata.get("rank"),
                    "rank_before_rerank": metadata.get("rank_before_rerank"),
                    "reranker": metadata.get("reranker"),
                    "query_intent": metadata.get("query_intent"),
                    "section_prior_score": metadata.get("section_prior_score"),
                    "rerank_score": metadata.get("rerank_score"),
                    "multi_query": metadata.get("multi_query"),
                    "matched_query_count": metadata.get("matched_query_count"),
                    "best_original_rank": metadata.get("best_original_rank"),
                },
            }
        )

    return {
        "count": len(retrieval_results),
        "preview_items": preview_items,
    }


def build_trace_from_state(state: PaperState) -> dict[str, Any]:
    chunks = state.get("chunks", [])
    retrieval_results = state.get("retrieval_results", [])

    return {
        "run_id": str(uuid.uuid4()),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "workflow": "paper_rag_report",
        "input": {
            "pdf_path": state.get("pdf_path"),
            "query": state.get("query"),
            "top_k": state.get("top_k"),
        },
        "config": {
            "retriever_type": state.get("retriever_type"),
            "embedding_model": state.get("embedding_model"),
            "faiss_index_dir": state.get("faiss_index_dir"),
            "rebuild_faiss_index": state.get("rebuild_faiss_index"),
            "use_query_expansion": state.get("use_query_expansion"),
            "query_expansion_max_queries": state.get("query_expansion_max_queries"),
            "multi_query_per_query_k": state.get("multi_query_per_query_k"),
            "multi_query_rrf_k": state.get("multi_query_rrf_k"),
            "retriever_candidate_k": state.get("retriever_candidate_k"),
            "reranker_type": state.get("reranker_type"),
            "reranker_top_k": state.get("reranker_top_k"),
            "retriever_weight": state.get("retriever_weight"),
            "hybrid_alpha": state.get("hybrid_alpha"),
        },
        "paper": {
            "paper_title": state.get("paper_title"),
            "raw_text": _text_summary(state.get("raw_text")),
            "paper_text": _text_summary(state.get("paper_text")),
            "chunks": _summarize_chunks(chunks),
        },
        "retrieval": {
            "expanded_queries": state.get("expanded_queries"),
            "retrieval_results": _summarize_retrieval_results(retrieval_results),
            "retrieved_context": _text_summary(state.get("retrieved_context")),
            "retrieval_evidence": _text_summary(state.get("retrieval_evidence")),
        },
        "llm_outputs": {
            "paper_summary": _text_summary(state.get("paper_summary")),
            "paper_critique": _text_summary(state.get("paper_critique")),
        },
        "llm_invocations": state.get("llm_invocations", []),
        "errors": state.get("errors", []),
        "outputs": {
            "report_path": state.get("output_path"),
            "final_report": _text_summary(state.get("final_report")),
        },
    }


def save_trace(
    state: PaperState,
    trace_dir: str = "outputs/traces",
) -> str:
    output_dir = Path(trace_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    trace_path = output_dir / f"trace_{timestamp}.json"

    trace = build_trace_from_state(state)
    trace["outputs"]["trace_path"] = str(trace_path)

    trace_path.write_text(
        json.dumps(trace, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return str(trace_path)
