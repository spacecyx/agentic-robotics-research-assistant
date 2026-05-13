from pathlib import Path
import argparse

from app.graph import build_graph
from app.states import PaperState


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Agentic Research Assistant for Robotics, SLAM, and 3D Perception Papers"
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
        default="What are the main problem, method, contribution, experimental results, and limitations of this paper?",
        help="Query used to retrieve relevant chunks from the paper.",
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of top retrieved chunks used as RAG context.",
    )

    # new add in Day 6
    # 选择 RAG 检索方式
    parser.add_argument(
        "--retriever-type",
        type=str,
        default="tfidf",
        choices=["tfidf", "embedding"],
        help="Retriever type used for RAG context retrieval.",
    )

    # 选择 embedding 模型
    parser.add_argument(
        "--embedding-model",
        type=str,
        default="sentence-transformers/all-MiniLM-L6-v2", 
        help="Embedding model name used by embedding retriever.",
    )

    return parser.parse_args()


# validate pdf path
def validate_pdf_path(pdf_path: str) -> Path:
    path = Path(pdf_path)

    # path check
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # suffix check
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Input file must be a PDF: {pdf_path}")
    
    return path


# print retrieval results
def print_retrieval_results(result: PaperState) -> None:
    print("========== RETRIEVED CHUNKS ==========\n")

    retrieval_results = result.get("retrieval_results", [])

    if not retrieval_results:
        print("No retrieval results found.\n")
        return

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
    

def main() -> None:
    args = parse_args()
    pdf_path = validate_pdf_path(args.pdf)

    graph = build_graph()

    initial_state: PaperState = {
        "pdf_path": str(pdf_path),      # for Day 5 has added validate_pdf_path(), which need str
        "query": args.query,
        "top_k": args.top_k,
        "retriever_type": args.retriever_type,
        "embedding_model": args.embedding_model,
    }

    # 展示选择的模型
    # print(f"Retriever type: {result.get('retriever_type', args.retriever_type)}")

    result = graph.invoke(initial_state)

    print("\n========== PAPER ANALYSIS FINISHED ==========\n")
    # print_retrieval_results(result)

    print("========== FINAL REPORT ==========\n")
    print(f"Report saved to: {result.get('output_path', '')}")


if __name__ == "__main__":
    main()