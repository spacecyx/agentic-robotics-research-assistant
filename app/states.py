from typing import TypedDict


# 定义 Agent 工作流里所有节点共享的数据结构
class PaperState(TypedDict):
    """
    State shared across the paper analysis workflow | LangGraph 中流转的状态对象
    """

    # Input
    pdf_path: str

    # PDF processing
    raw_text: str
    paper_text: str
    paper_title: str

    # LLM outputs
    paper_summary: str
    paper_critique: str

    # Final report
    final_report: str
    output_path: str