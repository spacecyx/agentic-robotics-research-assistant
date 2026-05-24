from app.states import PaperState
from app.tools.retrievers.factory import create_retriever


def format_retrieved_context(retrieval_results) -> str:
    context_blocks = []

    for rank, retrieval_result in enumerate(retrieval_results, start=1):
        chunk = retrieval_result.chunk
        score = retrieval_result.score

        block = (
            f"[Rank {rank} | Chunk ID: {chunk.chunk_id} | "
            f"Score: {score:.4f} | Char Range: {chunk.start_char}-{chunk.end_char}]\n"
            f"{chunk.text}"
        )

        context_blocks.append(block)

    return "\n\n".join(context_blocks)


def retrieve_context_node(state: PaperState) -> PaperState:
    print(">>> running retrieve_context_node")

    query = state["query"]
    chunks = state["chunks"]

    top_k = state.get("top_k", 5)
    retriever_type = state.get("retriever_type", "tfidf")       # default_type:tfidf
    embedding_model = state.get(
        "embedding_model",
        "sentence-transformers/all-MiniLM-L6-v2",
    )

    # 不再关心底层是 TF-IDF 还是 Embedding
    retriever = create_retriever(
        retriever_type=retriever_type,
        chunks=chunks,
        embedding_model=embedding_model,
    )

    retrieval_results = retriever.search(
        query=query,
        top_k=top_k,
    )

    retrieved_context = format_retrieved_context(retrieval_results)

    return {
        "retriever_type": retriever_type,
        "embedding_model": embedding_model,
        "retrieval_results": retrieval_results,
        "retrieved_context": retrieved_context,
    }
