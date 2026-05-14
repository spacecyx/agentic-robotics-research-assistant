# 测试 FAISS Retriever
# 运行方式：
# python -m scripts.test_faiss_retriever --pdf data/resnet.pdf --query "What is residual learning?"

from pathlib import Path
import argparse

from app.states import PaperState
from app.nodes.load_pdf import load_pdf_node
from app.nodes.split_text import split_text_node
from app.tools.retrievers.factory import create_retriever


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Test FAISS retriever on a paper PDF."
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
        help="Query used for FAISS retrieval.",
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of retrieved chunks.",
    )

    parser.add_argument(
        "--index-dir",
        type=str,
        default="",
        help="Directory of FAISS index files. Default: data/index/<pdf_stem>",
    )

    parser.add_argument(
        "--embedding-model",
        type=str,
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Embedding model name or local model path.",
    )

    parser.add_argument(
        "--rebuild-index",
        action="store_true",
        help="Rebuild FAISS index even if it already exists.",
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


def print_results(retrieval_results) -> None:
    for rank, retrieval_result in enumerate(retrieval_results, start=1):
        chunk = retrieval_result.chunk
        score = retrieval_result.score

        print("=" * 100)
        print(f"Rank: {rank}")
        print(f"Chunk ID: {chunk.chunk_id}")
        print(f"Score: {score:.4f}")
        print(f"Source: {retrieval_result.source}")
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

    index_dir = (
        args.index_dir
        if args.index_dir
        else str(Path("data/index") / pdf_path.stem)
    )

    chunks = prepare_chunks(str(pdf_path))

    retriever = create_retriever(
        retriever_type="faiss",
        chunks=chunks,
        embedding_model=args.embedding_model,
        faiss_index_dir=index_dir,
        rebuild_faiss_index=args.rebuild_index,
    )

    retrieval_results = retriever.search(
        query=args.query,
        top_k=args.top_k,
    )

    print("\n========== FAISS RETRIEVAL RESULTS ==========\n")
    print(f"PDF: {pdf_path}")
    print(f"Query: {args.query}")
    print(f"Top-K: {args.top_k}")
    print(f"Index dir: {index_dir}")
    print()

    print_results(retrieval_results)


if __name__ == "__main__":
    main()