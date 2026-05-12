# Retrieved Evidence support for final report

from pathlib import Path
import argparse

from app.graph import build_graph
from app.states import PaperState


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="End-to-end smoke test for the paper RAG pipeline."
    )

    parser.add_argument(
        "--pdf",
        type=str,
        default="data/resnet.pdf",
        help="Path to the test paper PDF.",
    )

    parser.add_argument(
        "--query",
        type=str,
        default="What is the main problem, method, contribution, and limitation of this paper?",
        help="Query used for retrieval.",
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of retrieved chunks.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        raise FileNotFoundError(f"Test PDF not found: {args.pdf}")

    graph = build_graph()

    initial_state: PaperState = {
        "pdf_path": str(pdf_path),
        "query": args.query,
        "top_k": args.top_k,
    }

    result = graph.invoke(initial_state)

    assert result.get("retrieval_results"), "Missing retrieval_results"
    assert result.get("retrieved_context"), "Missing retrieved_context"
    assert result.get("paper_summary"), "Missing paper_summary"
    assert result.get("paper_critique"), "Missing paper_critique"
    assert result.get("final_report"), "Missing final_report"
    assert result.get("output_path"), "Missing output_path"

    output_path = Path(result["output_path"])
    assert output_path.exists(), f"Report file does not exist: {output_path}"

    print("Pipeline test passed.")
    print(f"Report saved to: {output_path}")


if __name__ == "__main__":
    main()