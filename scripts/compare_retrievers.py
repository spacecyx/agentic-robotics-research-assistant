# 对比同一个 query 下 TF-IDF 和 Embedding 的检索结果
from pathlib import Path
import argparse

from app.states import PaperState
from app.nodes.load_pdf import load_pdf_node
from app.nodes.split_text import split_text_node
from app.tools.retrievers.factory import create_retriever


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare TF-IDF and embedding retrievers on the same paper query."
    )

    parser.add_argument(
        "--pdf",
        type=str,
        required=True,
        help="Path to the input paper PDF.",
    )

    parser.add_argument(
        "--query",
        type=str,
        required=True,
        help="Query used to compare retrievers.",
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of retrieved chunks.",
    )

    parser.add_argument(
        "--embedding-model",
        type=str,
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Embedding model name.",
    )

    # Day 7
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.6,
        help="Hybrid retrieval weight for embedding score. "
             "hybrid_score = alpha * embedding_score + (1 - alpha) * tfidf_score.",
    )

    parser.add_argument(
        "--candidate-k",
        type=int,
        default=20,
        help="Number of candidates retrieved from each retriever before hybrid fusion.",
    )

    return parser.parse_args()


def print_results(title: str, retrieval_results) -> None:
    print(f"\n========== {title} ==========\n")

    for rank, retrieval_result in enumerate(retrieval_results, start=1):
        chunk = retrieval_result.chunk
        score = retrieval_result.score

        print("=" * 100)
        print(f"Rank: {rank}")
        print(f"Chunk ID: {chunk.chunk_id}")
        print(f"Score: {score:.4f}")
        print(f"Char Range: {chunk.start_char} - {chunk.end_char}")
        print("-" * 100)
        print(chunk.text[:700])
        print()


# 复用 load_pdf_node 和 split_text_node
def prepare_chunks(pdf_path: str):
    state: PaperState = {
        "pdf_path": pdf_path,
    }

    loaded_state = load_pdf_node(state)
    state.update(loaded_state)

    split_state = split_text_node(state)
    state.update(split_state)

    return state["chunks"]


def main() -> None:
    args = parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {args.pdf}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Input file must be a PDF: {args.pdf}")

    chunks = prepare_chunks(str(pdf_path))

    tfidf_retriever = create_retriever(
        retriever_type="tfidf",
        chunks=chunks,
    )

    embedding_retriever = create_retriever(
        retriever_type="embedding",
        chunks=chunks,
        embedding_model=args.embedding_model,
    )

    hybrid_retriever = create_retriever(
        retriever_type="hybrid",
        chunks=chunks,
        embedding_model=args.embedding_model,
        alpha=args.alpha,
        candidate_k=args.candidate_k,
    )

    tfidf_results = tfidf_retriever.search(
        query=args.query,
        top_k=args.top_k,
    )

    embedding_results = embedding_retriever.search(
        query=args.query,
        top_k=args.top_k,
    )
    
    hybrid_results = hybrid_retriever.search(
        query=args.query,
        top_k=args.top_k,
    )

    print(f"PDF: {pdf_path}")
    print(f"Query: {args.query}")
    print(f"Top-K: {args.top_k}")
    print(f"Alpha: {args.alpha}")
    print(f"Candidate-K: {args.candidate_k}")

    print_results("TF-IDF RESULTS", tfidf_results)
    print_results("EMBEDDING RESULTS", embedding_results)
    print_results("HYBRID RESULTS", hybrid_results)


if __name__ == "__main__":
    main()