from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.nodes.generate_report import generate_report_node  # noqa: E402
from app.nodes.verify_evidence import verify_evidence_node  # noqa: E402
from app.tools.trace_writer import build_trace_from_state  # noqa: E402
from app.tools.retrievers.schemas import RetrievalResult  # noqa: E402
from app.tools.text_splitter import TextChunk  # noqa: E402


def make_result(text: str) -> RetrievalResult:
    chunk = TextChunk(
        chunk_id=2,
        text=text,
        start_char=0,
        end_char=len(text),
        page_start=1,
        page_end=1,
        section_title="Method",
    )

    return RetrievalResult(
        chunk=chunk,
        score=0.9,
        source="test",
        metadata={"rank": 1},
    )


def assert_verify_node_records_state() -> None:
    state = {
        "paper_summary": "FAST-LIO2 uses direct LiDAR-inertial odometry for real-time mapping.",
        "paper_critique": "The method is useful for low-latency robotic mapping systems.",
        "retrieval_results": [
            make_result(
                "FAST-LIO2 is a fast direct LiDAR-inertial odometry system for real-time mapping.",
            )
        ],
    }

    state.update(verify_evidence_node(state))

    assert state["summary_verification"]["num_claims_checked"] == 1
    assert state["summary_verification"]["method"] == "lexical_overlap"
    assert "weakly_supported_claims" in state
    assert "evidence_alignment_score" in state


def assert_fallback_generation_is_skipped() -> None:
    state = {
        "paper_summary": "[Fallback output: empty_retrieval_evidence. No sufficient retrieved evidence was available.]",
        "paper_critique": "[LLM generation failed in critique_paper_node: timeout. Please check trace log for details.]",
        "retrieval_results": [],
    }

    state.update(verify_evidence_node(state))

    assert state["summary_verification"]["status"] == "skipped"
    assert state["critique_verification"]["status"] == "skipped"
    assert state["evidence_alignment_score"] == 0.0


def assert_report_and_trace_include_verification() -> None:
    state = {
        "pdf_path": "data/verification-test.pdf",
        "query": "What method is used?",
        "top_k": 1,
        "paper_title": "Verification Test",
        "paper_summary": "FAST-LIO2 uses direct LiDAR-inertial odometry for real-time mapping.",
        "paper_critique": "The method uses a transformer decoder for language translation.",
        "retrieval_results": [
            make_result(
                "FAST-LIO2 is a fast direct LiDAR-inertial odometry system for real-time mapping.",
            )
        ],
        "retrieved_context": "context",
        "retrieval_evidence": "evidence",
        "disable_trace": True,
    }

    state.update(verify_evidence_node(state))
    state.update(generate_report_node(state))
    trace = build_trace_from_state(state)

    assert "Evidence Verification" in state["final_report"]
    assert "evidence_verification" in trace
    assert trace["evidence_verification"]["summary"]["method"] == "lexical_overlap"
    assert "weakly_supported_claims_count" in trace["evidence_verification"]


def main() -> None:
    assert_verify_node_records_state()
    print("verify node state fields passed")

    assert_fallback_generation_is_skipped()
    print("fallback verification skip passed")

    assert_report_and_trace_include_verification()
    print("report and trace verification output passed")

    print("All verify_evidence_node smoke tests passed.")


if __name__ == "__main__":
    main()
