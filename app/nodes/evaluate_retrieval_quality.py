from app.states import PaperState
from app.tools.query_understanding import classify_query_intent
from app.tools.retrieval_quality import evaluate_retrieval_quality


MAX_RETRIEVAL_RETRY_COUNT = 1


def evaluate_retrieval_quality_node(state: PaperState) -> PaperState:
    """
    Evaluate retrieval quality and decide the next graph branch.

    Conditional branching is opt-in. When disabled, this node records a
    disabled decision and routes to the original summarize path.
    """

    print(">>> running evaluate_retrieval_quality_node")

    if not state.get("enable_conditional_branch", False):
        return {
            "retrieval_retry_count": state.get("retrieval_retry_count", 0),
            "conditional_branch_decision": "disabled_proceed",
            "fallback_reason": "",
        }

    query = state.get("query", "")
    retrieval_results = state.get("retrieval_results", [])
    top_k = state.get("top_k", 5)
    retry_count = state.get("retrieval_retry_count", 0)
    query_intent = classify_query_intent(query)

    retrieval_quality = evaluate_retrieval_quality(
        query=query,
        retrieved_chunks=retrieval_results,
        top_k=top_k,
        query_intent=query_intent,
    )

    quality_label = retrieval_quality.get("quality_label", "weak")
    recommended_action = retrieval_quality.get("recommended_action", "expand_query")

    if quality_label == "empty" or recommended_action == "fallback":
        return {
            "retrieval_quality": retrieval_quality,
            "retrieval_retry_count": retry_count,
            "conditional_branch_decision": "fallback",
            "fallback_reason": "empty_retrieval_evidence",
        }

    if quality_label == "weak":
        if retry_count < MAX_RETRIEVAL_RETRY_COUNT and not state.get("use_query_expansion", False):
            return {
                "retrieval_quality": retrieval_quality,
                "retrieval_retry_count": retry_count + 1,
                "conditional_branch_decision": "retry_query_expansion",
                "fallback_reason": "",
                "use_query_expansion": True,
            }

        return {
            "retrieval_quality": retrieval_quality,
            "retrieval_retry_count": retry_count,
            "conditional_branch_decision": "proceed_with_warning",
            "fallback_reason": "weak_retrieval_evidence_after_retry",
        }

    return {
        "retrieval_quality": retrieval_quality,
        "retrieval_retry_count": retry_count,
        "conditional_branch_decision": "proceed",
        "fallback_reason": "",
    }


def route_after_retrieval_quality(state: PaperState) -> str:
    decision = state.get("conditional_branch_decision", "proceed")

    if decision == "retry_query_expansion":
        return "retry_retrieve_context"

    if decision == "fallback":
        return "fallback_generation"

    return "summarize_paper"
