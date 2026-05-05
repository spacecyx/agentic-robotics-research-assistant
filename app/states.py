from typing import TypedDict

# 定义 Agent 工作流里所有节点共享的数据结构
class ResearchState(TypedDict):
    """
    LangGraph 中流转的状态对象。

    Day 1 的最小状态：
    - paper_title: 论文标题
    - paper_abstract: 论文摘要
    - summary: 技术总结
    - critique: 批判性分析
    - report: 最终 Markdown 报告
    """

    paper_title: str
    paper_abstract: str
    summary: str
    critique: str
    report: str

    # 后续 Day 2 加 PDF，Day 4 加 RAG，都会继续扩展这个 State