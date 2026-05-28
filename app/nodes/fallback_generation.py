from app.states import PaperState


def fallback_generation_node(state: PaperState) -> PaperState:
    """
    Produce explicit fallback text when retrieval evidence is empty.

    This node avoids calling the LLM with an empty or meaningless context while
    still allowing the report node to generate a Markdown artifact.
    """

    print(">>> running fallback_generation_node")

    fallback_reason = state.get("fallback_reason", "retrieval_evidence_unavailable")

    fallback_message = (
        f"[Fallback output: {fallback_reason}. "
        "No sufficient retrieved evidence was available, so LLM summary and critique were skipped.]"
    )

    return {
        "paper_summary": fallback_message,
        "paper_critique": fallback_message,
    }
