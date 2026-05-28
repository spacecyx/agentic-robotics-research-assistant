from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.nodes.evaluate_retrieval_quality import (  # noqa: E402
    evaluate_retrieval_quality_node,
    route_after_retrieval_quality,
)
from app.nodes.fallback_generation import fallback_generation_node  # noqa: E402
from app.nodes.generate_report import generate_report_node  # noqa: E402
from app.nodes.verify_evidence import verify_evidence_node  # noqa: E402
from app.tools.trace_writer import build_trace_from_state  # noqa: E402
from app.tools.retrievers.schemas import RetrievalResult  # noqa: E402
from app.tools.text_splitter import TextChunk  # noqa: E402


def make_result(score: float = 0.0) -> RetrievalResult:
    chunk = TextChunk(
        chunk_id=0,
        text="This weak chunk has no dataset or metric evidence.",
        start_char=0,
        end_char=51,
        section_title="Method",
    )

    return RetrievalResult(
        chunk=chunk,
        score=score,
        source="test",
        metadata={"rank": 1},
    )


def assert_disabled_branch_routes_to_summarize() -> None:
    state = {
        "enable_conditional_branch": False,
        "retrieval_retry_count": 0,
    }
    update = evaluate_retrieval_quality_node(state)
    state.update(update)

    assert state["conditional_branch_decision"] == "disabled_proceed"
    assert route_after_retrieval_quality(state) == "summarize_paper"


def assert_weak_branch_retries_once() -> None:
    state = {
        "enable_conditional_branch": True,
        "query": "What dataset and metrics are used?",
        "retrieval_results": [make_result(score=0.8)],
        "top_k": 1,
        "retrieval_retry_count": 0,
        "use_query_expansion": False,
    }
    update = evaluate_retrieval_quality_node(state)
    state.update(update)

    assert state["conditional_branch_decision"] == "retry_query_expansion"
    assert state["retrieval_retry_count"] == 1
    assert state["use_query_expansion"] is True
    assert route_after_retrieval_quality(state) == "retry_retrieve_context"

    update = evaluate_retrieval_quality_node(state)
    state.update(update)

    assert state["conditional_branch_decision"] == "proceed_with_warning"
    assert state["retrieval_retry_count"] == 1
    assert route_after_retrieval_quality(state) == "summarize_paper"


def assert_empty_branch_fallback_report() -> None:
    state = {
        "enable_conditional_branch": True,
        "pdf_path": "data/missing-evidence.pdf",
        "query": "What sensors are used?",
        "top_k": 3,
        "paper_title": "Missing Evidence Test",
        "retrieval_results": [],
        "retrieved_context": "",
        "retrieval_evidence": "",
        "retrieval_retry_count": 0,
        "disable_trace": True,
    }
    state.update(evaluate_retrieval_quality_node(state))

    assert state["conditional_branch_decision"] == "fallback"
    assert route_after_retrieval_quality(state) == "fallback_generation"

    state.update(fallback_generation_node(state))
    state.update(verify_evidence_node(state))
    state.update(generate_report_node(state))

    assert state["summary_verification"]["status"] == "skipped"
    assert state["output_path"]
    assert "Retrieval Quality Warnings" in state["final_report"]
    assert "Retrieved context was empty" in state["final_report"]
    assert "Fallback output" in state["final_report"]


def assert_normal_path_report_has_no_warning() -> None:
    state = {
        "enable_conditional_branch": True,
        "pdf_path": "data/good-evidence.pdf",
        "query": "What is the main method?",
        "top_k": 1,
        "paper_title": "Good Evidence Test",
        "retrieval_results": [make_result(score=0.8)],
        "retrieved_context": "Relevant method evidence.",
        "retrieval_evidence": "Evidence metadata.",
        "retrieval_quality": {
            "quality_label": "good",
            "recommended_action": "proceed",
            "reasons": ["sufficient_retrieval_evidence"],
        },
        "conditional_branch_decision": "proceed",
        "retrieval_retry_count": 0,
        "fallback_reason": "",
        "paper_summary": "summary",
        "paper_critique": "critique",
        "disable_trace": True,
    }
    state.update(generate_report_node(state))

    assert "Retrieval Quality Warnings" not in state["final_report"]


def assert_trace_conditional_branch_summary() -> None:
    state = {
        "enable_conditional_branch": True,
        "use_query_expansion": True,
        "retrieval_quality": {
            "quality_label": "weak",
            "recommended_action": "expand_query",
            "reasons": ["low_top_score"],
        },
        "conditional_branch_decision": "proceed_with_warning",
        "retrieval_retry_count": 1,
        "fallback_reason": "weak_retrieval_evidence_after_retry",
    }
    trace = build_trace_from_state(state)
    branch = trace["retrieval"]["conditional_branch"]

    assert branch["enabled"] is True
    assert branch["quality_label"] == "weak"
    assert branch["recommended_action"] == "expand_query"
    assert branch["branch_decision"] == "proceed_with_warning"
    assert branch["retry_count"] == 1
    assert branch["fallback_reason"] == "weak_retrieval_evidence_after_retry"
    assert branch["query_expansion_used"] is True


def main() -> None:
    assert_disabled_branch_routes_to_summarize()
    print("disabled branch route passed")

    assert_weak_branch_retries_once()
    print("weak branch retry limit passed")

    assert_empty_branch_fallback_report()
    print("empty branch fallback report passed")

    assert_normal_path_report_has_no_warning()
    print("normal path report warning suppression passed")

    assert_trace_conditional_branch_summary()
    print("trace conditional branch summary passed")

    print("All conditional branch smoke tests passed.")


if __name__ == "__main__":
    main()
