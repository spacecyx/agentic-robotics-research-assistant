from typing import Any

from app.states import PaperState
from app.tools.evidence_verifier import verify_text_against_evidence


def verify_evidence_node(state: PaperState) -> PaperState:
    """
    Verify generated summary and critique against retrieved evidence chunks.

    This is a weak lexical evidence alignment check, not strict fact-checking.
    It should never block report generation.
    """

    print(">>> running verify_evidence_node")

    retrieval_results = state.get("retrieval_results", [])
    paper_summary = state.get("paper_summary", "")
    paper_critique = state.get("paper_critique", "")

    summary_verification = _verify_generated_text(
        generated_text=paper_summary,
        evidence_chunks=retrieval_results,
        source_field="paper_summary",
    )
    critique_verification = _verify_generated_text(
        generated_text=paper_critique,
        evidence_chunks=retrieval_results,
        source_field="paper_critique",
    )

    weakly_supported_claims = (
        _tag_claim_source(summary_verification.get("weakly_supported_claims", []), "paper_summary")
        + _tag_claim_source(critique_verification.get("weakly_supported_claims", []), "paper_critique")
    )
    evidence_alignment_score = _compute_alignment_score(
        summary_verification=summary_verification,
        critique_verification=critique_verification,
    )

    return {
        "summary_verification": summary_verification,
        "critique_verification": critique_verification,
        "weakly_supported_claims": weakly_supported_claims,
        "evidence_alignment_score": evidence_alignment_score,
    }


def _verify_generated_text(
    generated_text: str,
    evidence_chunks: list[Any],
    source_field: str,
) -> dict[str, Any]:
    if _should_skip_verification(generated_text):
        return {
            "num_claims_checked": 0,
            "supported_claims": [],
            "weakly_supported_claims": [],
            "avg_support_score": 0.0,
            "method": "lexical_overlap",
            "status": "skipped",
            "source_field": source_field,
            "skip_reason": "fallback_or_failed_generation",
        }

    result = verify_text_against_evidence(
        generated_text=generated_text,
        evidence_chunks=evidence_chunks,
    )
    result["source_field"] = source_field

    return result


def _should_skip_verification(generated_text: str) -> bool:
    stripped_text = (generated_text or "").strip()

    if not stripped_text:
        return True

    return (
        stripped_text.startswith("[Fallback output:")
        or stripped_text.startswith("[LLM generation failed")
    )


def _tag_claim_source(
    claim_results: list[dict[str, Any]],
    source_field: str,
) -> list[dict[str, Any]]:
    tagged_results = []

    for claim_result in claim_results:
        tagged_result = dict(claim_result)
        tagged_result["source_field"] = source_field
        tagged_results.append(tagged_result)

    return tagged_results


def _compute_alignment_score(
    summary_verification: dict[str, Any],
    critique_verification: dict[str, Any],
) -> float:
    scores = []

    for verification in (summary_verification, critique_verification):
        if verification.get("status") in {"skipped", "no_claims_extracted"}:
            continue

        scores.append(float(verification.get("avg_support_score", 0.0) or 0.0))

    if not scores:
        return 0.0

    return float(sum(scores) / len(scores))
