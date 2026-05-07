from pathlib import Path
import argparse

from app.graph import build_graph
from app.states import PaperState

# test branch
def main():
    parser = argparse.ArgumentParser(
        description="Agentic Research Assistant for Robotics & 3D Perception"
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
        default="What are the main problem, method, contribution, and experimental results of this paper?",
        help="Query used to retrieve relevant chunks from the paper.",
    )

    args = parser.parse_args()

    graph = build_graph()

    # initial_state: PaperState = {
    # "pdf_path": args.pdf,
    # "raw_text": "",
    # "paper_text": "",
    # "paper_title": "",
    # "paper_summary": "",
    # "paper_critique": "",
    # "final_report": "",
    # "output_path": "",
    # }

    initial_state: PaperState = {
        "pdf_path": args.pdf,
        "query": args.query,
    }

    result = graph.invoke(initial_state)

    # print("\n========== PAPER ANALYSIS FINISHED ==========\n")
    # print(f"Report saved to: {result['output_path']}")

    print("\n========== PAPER ANALYSIS FINISHED ==========\n")

    print("========== RETRIEVED CHUNKS ==========\n")
    # for rank, retrieval_result in enumerate(result.get("retrieval_results", []), start=1):  # 从 1 开始
    #     chunk = retrieval_result.chunk
    #     score = retrieval_result.score

    #     print("=" * 100)
    #     print(f"Rank: {rank}")
    #     print(f"Chunk ID: {chunk.chunk_id}")
    #     print(f"Score: {score:.4f}")
    #     print(f"Char Range: {chunk.start_char} - {chunk.end_char}")
    #     print("-" * 100)
    #     print(chunk.text[:700])
    #     print()

    print("========== FINAL REPORT ==========\n")
    print(f"Report saved to: {result.get('output_path', '')}")


if __name__ == "__main__":
    main()