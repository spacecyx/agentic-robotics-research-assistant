# 报告生成节点
from app.states import ResearchState

# 该节点故意不调用模型 | 不是每个节点都必须调用 LLM
# 有些节点负责工具调用，有些节点负责格式化，有些节点负责路由，这是 Agent 工程中很重要的设计思想
def generate_report_node(state: ResearchState) -> dict:
    """
    节点 3：生成最终 Markdown 报告。
    这里不调用 LLM，只负责格式化。
    """

    report = f"""# Paper Analysis Report

## Paper Title

{state["paper_title"]}

## Abstract

{state["paper_abstract"]}

## 1. Technical Summary

{state["summary"]}

## 2. Critical Analysis

{state["critique"]}

## 3. Day 1 Project Value

当前 Day 1 已经完成一个最小 LangGraph Agent 工作流：

- 使用 ResearchState 管理中间状态
- 使用 summarize_paper_node 完成论文摘要总结
- 使用 critique_paper_node 完成批判性分析
- 使用 generate_report_node 生成结构化 Markdown 报告
- 使用 StateGraph 编排多节点执行流程

这为后续扩展打下基础：

- Day 2：加入 PDF 解析
- Day 3：规范 Prompt 与报告模板
- Day 4：加入 RAG 检索
- Day 5：加入 GitHub README / Repo 分析
- Day 6：串联 Paper Agent 与 Repo Agent
"""

    return {
        "report": report,
    }