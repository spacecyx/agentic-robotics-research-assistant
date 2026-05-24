from app.states import PaperState
from app.tools.simple_retriever import retrieve_top_k, RetrievalResult


def format_retrieval_results(results: list[RetrievalResult]) -> str:
    """
    Format retrieved chunks into a prompt-friendly context string.
    """

    formatted_chunks: list[str] = []

    for rank, result in enumerate(results, start=1):
        chunk = result.chunk

        formatted_chunks.append(
            f"[Rank {rank} | Chunk {chunk.chunk_id} | Score: {result.score:.4f} | "
            f"Char Range: {chunk.start_char}-{chunk.end_char}]\n"
            f"{chunk.text}"
        )

    return "\n\n".join(formatted_chunks)


def retrieve_context_node(state: PaperState) -> dict:
    """
    Retrieve top-k relevant chunks based on the user query.
    """
    print(">>> running retrieve_context_node")

    query = state.get("query", "").strip()
    chunks = state.get("chunks", [])

    if not query:
        raise ValueError("query must not be empty. Please provide a query in initial_state.")

    if not chunks:
        raise ValueError("No chunks found in state. Please check split_text_node output.")

    retrieval_results = retrieve_top_k(
        query=query,
        chunks=chunks,
        top_k=3,
    )

    retrieved_context = format_retrieval_results(retrieval_results)

    return {
        "retrieval_results": retrieval_results,     # 保留结构化检索结果，方便调试
        "retrieved_context": retrieved_context,     # 转成字符串，方便后续 LLM prompt 使用
    }
