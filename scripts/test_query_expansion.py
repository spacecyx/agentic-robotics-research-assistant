# 测试 Query Expansion + MultiQueryRetriever
# 运行方式：
# python -m scripts.test_query_expansion --pdf data/resnet.pdf --query "What are the main method and limitations of ResNet?"

from pathlib import Path
import argparse

from app.states import PaperState
from app.nodes.load_pdf import load_pdf_node
from app.nodes.split_text import split_text_node
from app.tools.retrievers.factory import create_retriever
from app.tools.retrievers.multi_query_retriever import MultiQueryRetriever
from app.tools.query_expansion import HeuristicQueryExpander


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Test query expansion and multi-query retrieval."
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
        help="Original query.",
    )

    parser.add_argument(
        "--retriever-type",
        type=str,
        default="tfidf",
        choices=["tfidf", "embedding", "hybrid", "faiss"],
        help="Base retriever type.",
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Final number of retrieved chunks.",
    )

    parser.add_argument(
        "--per-query-k",
        type=int,
        default=8,
        help="Number of retrieved chunks for each expanded query.",
    )

    parser.add_argument(
        "--max-queries",
        type=int,
        default=4,
        help="Maximum number of expanded queries.",
    )

    parser.add_argument(
        "--embedding-model",
        type=str,
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Embedding model name or local model path.",
    )

    parser.add_argument(
        "--alpha",
        type=float,
        default=0.6,
        help="Hybrid retrieval alpha.",
    )

    parser.add_argument(
        "--faiss-index-dir",
        type=str,
        default="",
        help="FAISS index directory.",
    )

    return parser.parse_args()


def prepare_chunks(pdf_path: str):
    state: PaperState = {
        "pdf_path": pdf_path,
    }

    loaded_state = load_pdf_node(state)
    state.update(loaded_state)

    split_state = split_text_node(state)
    state.update(split_state)

    return state["chunks"]


def print_results(title: str, retrieval_results) -> None:
    print(f"\n========== {title} ==========\n")

    for rank, result in enumerate(retrieval_results, start=1):
        chunk = result.chunk

        print("=" * 100)
        print(f"Rank: {rank}")
        print(f"Chunk ID: {chunk.chunk_id}")
        print(f"Score: {result.score:.4f}")
        print(f"Source: {result.source}")
        print(f"Matched Query Count: {result.metadata.get('matched_query_count', 'N/A')}")
        print(f"Original Ranks: {result.metadata.get('original_ranks', 'N/A')}")
        print(f"Char Range: {chunk.start_char} - {chunk.end_char}")
        print("-" * 100)
        print(chunk.text[:800])
        print()


def main() -> None:
    args = parse_args()

    pdf_path = Path(args.pdf)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {args.pdf}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Input file must be a PDF: {args.pdf}")

    chunks = prepare_chunks(str(pdf_path))

    base_retriever = create_retriever(
        retriever_type=args.retriever_type,
        chunks=chunks,
        embedding_model=args.embedding_model,
        alpha=args.alpha,
        candidate_k=args.per_query_k,
        faiss_index_dir=args.faiss_index_dir or None,
    )

    query_expander = HeuristicQueryExpander()

    multi_query_retriever = MultiQueryRetriever(
        base_retriever=base_retriever,
        query_expander=query_expander,
        max_queries=args.max_queries,
        per_query_k=args.per_query_k,
    )

    original_results = base_retriever.search(
        query=args.query,
        top_k=args.top_k,
    )

    multi_query_results = multi_query_retriever.search(
        query=args.query,
        top_k=args.top_k,
    )

    print("\n========== EXPANDED QUERIES ==========\n")
    for index, expanded_query in enumerate(multi_query_retriever.last_expanded_queries, start=1):
        print(f"{index}. {expanded_query}")

    print_results("ORIGINAL QUERY RESULTS", original_results)
    print_results("MULTI-QUERY RESULTS", multi_query_results)


if __name__ == "__main__":
    main()