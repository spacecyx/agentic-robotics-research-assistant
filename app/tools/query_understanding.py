"""
Lightweight query intent understanding for paper-reading RAG workflows.

The classifier is intentionally rule-based so retrieval and evaluation remain
deterministic and do not require an LLM call.
"""

from __future__ import annotations


INTENT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "contribution": (
        "contribution",
        "contributions",
        "novelty",
        "propose",
        "proposed",
        "key idea",
        "main idea",
    ),
    "problem": (
        "problem",
        "challenge",
        "challenges",
        "motivation",
        "why",
    ),
    "method": (
        "method",
        "methods",
        "approach",
        "algorithm",
        "framework",
        "pipeline",
    ),
    "architecture": (
        "architecture",
        "module",
        "network",
        "block",
        "layer",
        "layers",
    ),
    "experiment": (
        "experiment",
        "experiments",
        "evaluation",
        "compare",
        "comparison",
        "baseline",
        "baselines",
    ),
    "result": (
        "result",
        "results",
        "performance",
        "accuracy",
        "improvement",
        "score",
        "scores",
    ),
    "limitation": (
        "limitation",
        "limitations",
        "weakness",
        "weaknesses",
        "drawback",
        "drawbacks",
        "failure",
        "failures",
        "future work",
    ),
    "related_work": (
        "related work",
        "prior work",
        "previous methods",
        "previous method",
    ),
    "dataset": (
        "dataset",
        "datasets",
        "benchmark",
        "benchmarks",
        "data",
    ),
    "metric": (
        "metric",
        "metrics",
        "map",
        "bleu",
        "accuracy",
        "recall",
        "precision",
    ),
    "implementation": (
        "implementation",
        "training",
        "hyperparameter",
        "hyperparameters",
        "learning rate",
        "batch size",
    ),
}


PREFERRED_SECTIONS: dict[str, list[str]] = {
    "contribution": ["Abstract", "Introduction", "Conclusion"],
    "problem": ["Abstract", "Introduction"],
    "method": ["Method", "Methods", "Approach", "Model", "Deep Residual Learning"],
    "architecture": ["Method", "Architecture", "Network", "Deep Residual Learning"],
    "experiment": ["Experiments", "Evaluation", "Results"],
    "result": ["Experiments", "Results"],
    "limitation": ["Discussion", "Conclusion", "Limitations"],
    "related_work": ["Related Work", "Background"],
    "dataset": ["Experiments", "Dataset", "Evaluation"],
    "metric": ["Experiments", "Results", "Evaluation"],
    "implementation": ["Implementation", "Training", "Experiments"],
    "general": [],
}


def classify_query_intent(query: str) -> str:
    """
    Classify a paper-reading query into a coarse intent label.

    If no keyword rule matches, return ``general``.
    """

    normalized_query = query.lower()

    for intent, keywords in INTENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in normalized_query:
                return intent

    return "general"


def get_preferred_sections(intent: str) -> list[str]:
    """
    Return preferred paper sections for a query intent.
    """

    return PREFERRED_SECTIONS.get(intent, [])


def compute_section_prior_score(
    section_title: str | None,
    preferred_sections: list[str],
) -> float:
    """
    Score whether a chunk section matches the preferred sections.
    """

    if not section_title or not preferred_sections:
        return 0.0

    normalized_section = section_title.lower()

    for preferred_section in preferred_sections:
        normalized_preferred = preferred_section.lower()

        if normalized_section == normalized_preferred:
            return 1.0

    for preferred_section in preferred_sections:
        normalized_preferred = preferred_section.lower()

        if (
            normalized_preferred in normalized_section
            or normalized_section in normalized_preferred
        ):
            return 0.7

    return 0.0
