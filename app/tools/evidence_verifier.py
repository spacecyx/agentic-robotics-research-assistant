"""
Lightweight weak evidence alignment for generated text.

This module does not perform strict fact-checking. It only checks whether
generated claim-like sentences have lexical support in retrieved evidence
chunks, so results should be interpreted as weak support signals.
"""

from __future__ import annotations

import re
from typing import Any


METHOD = "lexical_overlap"
MIN_CLAIM_CHARS = 20
SUPPORTED_THRESHOLD = 0.32
WEAKLY_SUPPORTED_THRESHOLD = 0.12

STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then",
    "is", "are", "was", "were", "be", "been", "being",
    "of", "to", "in", "on", "for", "with", "by", "as", "at", "from",
    "this", "that", "these", "those", "it", "its", "they", "their",
    "paper", "section", "summary", "critique", "analysis",
    "the", "主要", "本文", "论文", "方法", "指出", "说明",
}

STRUCTURAL_PREFIXES = (
    "#",
    "-",
    "*",
    "论文摘要",
    "论文批判性分析",
    "必须掌握的内容",
    "建议掌握的内容",
    "可以暂缓的内容",
)


def verify_text_against_evidence(
    generated_text: str,
    evidence_chunks: list[Any],
    max_claims: int = 8,
) -> dict[str, Any]:
    """
    Check generated text against retrieved evidence chunks with lexical overlap.

    Args:
        generated_text: Summary, critique, or other generated output.
        evidence_chunks: RetrievalResult-like objects or chunk-like objects.
        max_claims: Maximum number of claim sentences to check.

    Returns:
        A structured weak support report. The function catches internal errors
        and returns a non-raising failure result.
    """

    try:
        claims = extract_claim_sentences(
            generated_text=generated_text,
            max_claims=max_claims,
        )
        evidence_items = [_build_evidence_item(item) for item in evidence_chunks]
        evidence_items = [item for item in evidence_items if item["text"].strip()]

        if not claims:
            return _empty_result(
                num_claims_checked=0,
                reason="no_claims_extracted",
            )

        if not evidence_items:
            return {
                "num_claims_checked": len(claims),
                "supported_claims": [],
                "weakly_supported_claims": [
                    _build_claim_result(
                        claim=claim,
                        support_label="weakly_supported",
                        support_score=0.0,
                        best_matching_chunk=None,
                    )
                    for claim in claims
                ],
                "avg_support_score": 0.0,
                "method": METHOD,
                "status": "no_evidence_chunks",
            }

        supported_claims: list[dict[str, Any]] = []
        weakly_supported_claims: list[dict[str, Any]] = []
        support_scores: list[float] = []

        for claim in claims:
            best_match = _find_best_evidence_match(
                claim=claim,
                evidence_items=evidence_items,
            )
            support_score = best_match["support_score"]
            support_scores.append(support_score)

            support_label = _label_support_score(support_score)
            claim_result = _build_claim_result(
                claim=claim,
                support_label=support_label,
                support_score=support_score,
                best_matching_chunk=best_match["evidence"],
            )

            if support_label == "supported":
                supported_claims.append(claim_result)
            else:
                weakly_supported_claims.append(claim_result)

        avg_support_score = (
            sum(support_scores) / len(support_scores)
            if support_scores
            else 0.0
        )

        return {
            "num_claims_checked": len(claims),
            "supported_claims": supported_claims,
            "weakly_supported_claims": weakly_supported_claims,
            "avg_support_score": float(avg_support_score),
            "method": METHOD,
            "status": "ok",
        }
    except Exception as error:
        return {
            "num_claims_checked": 0,
            "supported_claims": [],
            "weakly_supported_claims": [],
            "avg_support_score": 0.0,
            "method": METHOD,
            "status": "verification_failed",
            "error_message": str(error),
        }


def extract_claim_sentences(
    generated_text: str,
    max_claims: int = 8,
) -> list[str]:
    if not generated_text or not generated_text.strip() or max_claims <= 0:
        return []

    normalized_text = _strip_markdown_markup(generated_text)
    candidates = re.split(r"(?<=[。！？!?\.])\s+|\n+", normalized_text)

    claims: list[str] = []

    for candidate in candidates:
        claim = " ".join(candidate.strip().split())

        if not _is_claim_like_sentence(claim):
            continue

        claims.append(claim)

        if len(claims) >= max_claims:
            break

    return claims


def compute_lexical_support_score(claim: str, evidence_text: str) -> float:
    claim_tokens = _tokenize(claim)
    evidence_tokens = _tokenize(evidence_text)

    if not claim_tokens or not evidence_tokens:
        return 0.0

    claim_set = set(claim_tokens)
    evidence_set = set(evidence_tokens)
    overlap = claim_set & evidence_set

    if not overlap:
        return 0.0

    coverage = len(overlap) / len(claim_set)
    jaccard = len(overlap) / len(claim_set | evidence_set)

    return float((0.75 * coverage) + (0.25 * jaccard))


def _find_best_evidence_match(
    claim: str,
    evidence_items: list[dict[str, Any]],
) -> dict[str, Any]:
    best_evidence: dict[str, Any] | None = None
    best_score = 0.0

    for evidence in evidence_items:
        support_score = compute_lexical_support_score(
            claim=claim,
            evidence_text=evidence["text"],
        )

        if support_score > best_score:
            best_score = support_score
            best_evidence = evidence

    return {
        "support_score": float(best_score),
        "evidence": best_evidence,
    }


def _build_evidence_item(item: Any) -> dict[str, Any]:
    chunk = getattr(item, "chunk", item)
    result_score = getattr(item, "score", None)

    return {
        "chunk_id": getattr(chunk, "chunk_id", None),
        "text": str(getattr(chunk, "text", "") or ""),
        "retrieval_score": result_score,
        "page_range": [
            getattr(chunk, "page_start", None),
            getattr(chunk, "page_end", None),
        ],
        "section": getattr(chunk, "section_title", None),
        "source": getattr(item, "source", ""),
    }


def _build_claim_result(
    claim: str,
    support_label: str,
    support_score: float,
    best_matching_chunk: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "claim": claim,
        "support_label": support_label,
        "support_score": float(support_score),
        "best_matching_chunk": best_matching_chunk,
    }


def _label_support_score(score: float) -> str:
    if score >= SUPPORTED_THRESHOLD:
        return "supported"

    if score >= WEAKLY_SUPPORTED_THRESHOLD:
        return "weakly_supported"

    return "weakly_supported"


def _empty_result(
    num_claims_checked: int,
    reason: str,
) -> dict[str, Any]:
    return {
        "num_claims_checked": num_claims_checked,
        "supported_claims": [],
        "weakly_supported_claims": [],
        "avg_support_score": 0.0,
        "method": METHOD,
        "status": reason,
    }


def _strip_markdown_markup(text: str) -> str:
    lines = []

    for line in text.splitlines():
        stripped = line.strip()

        if not stripped:
            continue

        if any(stripped.startswith(prefix) for prefix in STRUCTURAL_PREFIXES):
            continue

        stripped = re.sub(r"^\d+[\.\)]\s*", "", stripped)
        stripped = stripped.strip("`*_ ")
        lines.append(stripped)

    return "\n".join(lines)


def _is_claim_like_sentence(sentence: str) -> bool:
    if len(sentence) < MIN_CLAIM_CHARS:
        return False

    if sentence.startswith("[Fallback output:") or sentence.startswith("[LLM generation failed"):
        return False

    if any(sentence.startswith(prefix) for prefix in STRUCTURAL_PREFIXES):
        return False

    return bool(_tokenize(sentence))


def _tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[A-Za-z0-9_\-]+", text.lower())

    return [
        token
        for token in tokens
        if token not in STOP_WORDS and len(token) > 1
    ]
