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

    args = parser.parse_args()

    graph = build_graph()

    initial_state: PaperState = {
    "pdf_path": args.pdf,
    "raw_text": "",
    "paper_text": "",
    "paper_title": "",
    "paper_summary": "",
    "paper_critique": "",
    "final_report": "",
    "output_path": "",
    }

    result = graph.invoke(initial_state)

    print("\n========== PAPER ANALYSIS FINISHED ==========\n")
    print(f"Report saved to: {result['output_path']}")



if __name__ == "__main__":
    main()