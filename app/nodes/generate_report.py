# 报告生成节点
# 该节点故意不调用模型 | 不是每个节点都必须调用 LLM
# 有些节点负责工具调用，有些节点负责格式化，有些节点负责路由，这是 Agent 工程中很重要的设计思想

from datetime import datetime
from pathlib import Path

from app.states import PaperState


def generate_report_node(state: PaperState) -> PaperState:
    """
    LangGraph node:
    Generate and save a Markdown report.
    """
    print(">>> running generate_report_node")
    
    pdf_path = Path(state["pdf_path"])
    file_name = pdf_path.stem
    paper_title = state["paper_title"]

    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"{file_name}_report_{timestamp}.md"

    final_report = f"""# Paper Analysis Report

## Paper Title

{paper_title}

## Source PDF

{state["pdf_path"]}

---

{state["paper_summary"]}

---

{state["paper_critique"]}
"""

    output_path.write_text(final_report, encoding="utf-8")

    return {
        **state,
        "final_report": final_report,
        "output_path": str(output_path),
    }