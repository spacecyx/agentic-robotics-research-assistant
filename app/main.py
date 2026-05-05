from pathlib import Path

from app.graph import build_graph
from app.states import ResearchState

# test branch
def main():
    graph = build_graph()

    # 测试 transformer 论文
    initial_state: ResearchState = {
        "paper_title": "Attention Is All You Need",
        "paper_abstract": """
The dominant sequence transduction models are based on complex recurrent or convolutional neural networks.
We propose a new simple network architecture, the Transformer, based solely on attention mechanisms,
dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show
these models to be superior in quality while being more parallelizable and requiring significantly less time to train.
""",
        "summary": "",
        "critique": "",
        "report": "",
    }

    final_state = graph.invoke(initial_state)

    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / "day1_report.md"
    output_path.write_text(final_state["report"], encoding="utf-8")

    print(final_state["report"])
    print(f"\nReport saved to: {output_path}")


if __name__ == "__main__":
    main()