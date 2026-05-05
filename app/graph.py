from langgraph.graph import StateGraph, END

from app.states import ResearchState
from app.nodes.summarize_paper import summarize_paper_node
from app.nodes.critique_paper import critique_paper_node
from app.nodes.generate_report import generate_report_node


def build_graph():
    """
    构建 Day 1 最小 LangGraph 工作流。

    执行流程：
    summarize_paper -> critique_paper -> generate_report -> END
    """

    # 创建一个状态图
    builder = StateGraph(ResearchState)

    # add_node 添加计算节点
    builder.add_node("summarize_paper", summarize_paper_node)
    builder.add_node("critique_paper", critique_paper_node)
    builder.add_node("generate_report", generate_report_node)

    # 表示第一个执行的节点 | 等价于从 START 指向指定节点
    builder.set_entry_point("summarize_paper")

    # 定义节点执行顺序
    builder.add_edge("summarize_paper", "critique_paper")
    builder.add_edge("critique_paper", "generate_report")
    builder.add_edge("generate_report", END)

    # 编译成可执行图
    return builder.compile()