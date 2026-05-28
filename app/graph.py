from langgraph.graph import StateGraph, END

from app.states import PaperState
from app.nodes.load_pdf import load_pdf_node
from app.nodes.split_text import split_text_node
from app.nodes.retrieve_context import retrieve_context_node
from app.nodes.evaluate_retrieval_quality import (
    evaluate_retrieval_quality_node,
    route_after_retrieval_quality,
)
from app.nodes.summarize_paper import summarize_paper_node
from app.nodes.critique_paper import critique_paper_node
from app.nodes.fallback_generation import fallback_generation_node
from app.nodes.verify_evidence import verify_evidence_node
from app.nodes.generate_report import generate_report_node



def build_graph():
    """
    构建 Day 1 最小 LangGraph 工作流 

    执行流程：
    summarize_paper -> critique_paper -> generate_report -> END
    """
    """
    Build the Day 2 paper analysis workflow.

    Workflow:
    load_pdf -> summarize_paper -> critique_paper -> generate_report -> END

    Build the Day 4 RAG-style paper analysis workflow.

    Workflow:
    load_pdf -> split_text -> retrieve_context -> summarize_paper
    -> critique_paper -> generate_report -> END
    """

    # 创建一个状态图
    builder = StateGraph(PaperState)

    # add_node 添加计算节点
    builder.add_node("load_pdf", load_pdf_node)
    builder.add_node("split_text", split_text_node)
    builder.add_node("retrieve_context", retrieve_context_node)
    builder.add_node("evaluate_retrieval_quality", evaluate_retrieval_quality_node)
    builder.add_node("summarize_paper", summarize_paper_node)
    builder.add_node("critique_paper", critique_paper_node)
    builder.add_node("fallback_generation", fallback_generation_node)
    builder.add_node("verify_evidence", verify_evidence_node)
    builder.add_node("generate_report", generate_report_node)

    # 表示第一个执行的节点 | 等价于从 START 指向指定节点
    builder.set_entry_point("load_pdf")

    # 定义节点执行顺序 | 保留默认线性路径，并在 retrieval 后加入可选条件分支
    builder.add_edge("load_pdf", "split_text")
    builder.add_edge("split_text", "retrieve_context")
    builder.add_edge("retrieve_context", "evaluate_retrieval_quality")
    builder.add_conditional_edges(
        "evaluate_retrieval_quality",
        route_after_retrieval_quality,
        {
            "retry_retrieve_context": "retrieve_context",
            "fallback_generation": "fallback_generation",
            "summarize_paper": "summarize_paper",
        },
    )
    builder.add_edge("summarize_paper", "critique_paper")
    builder.add_edge("critique_paper", "verify_evidence")
    builder.add_edge("fallback_generation", "verify_evidence")
    builder.add_edge("verify_evidence", "generate_report")
    builder.add_edge("generate_report", END)

    # 编译成可执行图
    return builder.compile()
