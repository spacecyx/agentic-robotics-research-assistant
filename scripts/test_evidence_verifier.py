from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.tools.evidence_verifier import verify_text_against_evidence  # noqa: E402
from app.tools.retrievers.schemas import RetrievalResult  # noqa: E402
from app.tools.text_splitter import TextChunk  # noqa: E402


def make_result(
    chunk_id: int,
    text: str,
    score: float = 0.9,
    section_title: str | None = "Method",
) -> RetrievalResult:
    chunk = TextChunk(
        chunk_id=chunk_id,
        text=text,
        start_char=0,
        end_char=len(text),
        page_start=1,
        page_end=1,
        section_title=section_title,
    )

    return RetrievalResult(
        chunk=chunk,
        score=score,
        source="test",
        metadata={"rank": 1},
    )


def assert_supported_claim() -> None:
    generated_text = (
        "FAST-LIO2 uses direct LiDAR-inertial odometry for real-time mapping."
    )
    evidence = [
        make_result(
            3,
            "FAST-LIO2 is a fast direct LiDAR-inertial odometry system for real-time mapping.",
        )
    ]

    result = verify_text_against_evidence(
        generated_text=generated_text,
        evidence_chunks=evidence,
    )

    assert result["status"] == "ok"
    assert result["num_claims_checked"] == 1
    assert len(result["supported_claims"]) == 1
    claim = result["supported_claims"][0]
    assert claim["best_matching_chunk"]["chunk_id"] == 3
    assert claim["support_score"] > 0.32


def assert_unrelated_claim_is_weak() -> None:
    generated_text = "The paper proposes a transformer decoder for natural language translation."
    evidence = [
        make_result(
            4,
            "FAST-LIO2 is a fast direct LiDAR-inertial odometry system for real-time mapping.",
        )
    ]

    result = verify_text_against_evidence(
        generated_text=generated_text,
        evidence_chunks=evidence,
    )

    assert result["status"] == "ok"
    assert result["num_claims_checked"] == 1
    assert len(result["supported_claims"]) == 0
    assert len(result["weakly_supported_claims"]) == 1
    claim = result["weakly_supported_claims"][0]
    assert claim["support_score"] == 0.0
    assert claim["best_matching_chunk"] is None


def assert_empty_generated_text() -> None:
    result = verify_text_against_evidence(
        generated_text="",
        evidence_chunks=[
            make_result(1, "LiDAR odometry evidence."),
        ],
    )

    assert result["status"] == "no_claims_extracted"
    assert result["num_claims_checked"] == 0
    assert result["supported_claims"] == []
    assert result["weakly_supported_claims"] == []


def assert_empty_evidence_chunks() -> None:
    result = verify_text_against_evidence(
        generated_text="FAST-LIO2 uses LiDAR-inertial odometry for mapping.",
        evidence_chunks=[],
    )

    assert result["status"] == "no_evidence_chunks"
    assert result["num_claims_checked"] == 1
    assert result["supported_claims"] == []
    assert len(result["weakly_supported_claims"]) == 1
    assert result["weakly_supported_claims"][0]["best_matching_chunk"] is None


def main() -> None:
    assert_supported_claim()
    print("supported claim passed")

    assert_unrelated_claim_is_weak()
    print("unrelated claim weak support passed")

    assert_empty_generated_text()
    print("empty generated text passed")

    assert_empty_evidence_chunks()
    print("empty evidence chunks passed")

    print("All evidence_verifier smoke tests passed.")


if __name__ == "__main__":
    main()
