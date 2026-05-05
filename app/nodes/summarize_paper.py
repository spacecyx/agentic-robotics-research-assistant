from app.states import ResearchState
from app.tools.llm_client import get_llm

# 论文总结节点
def summarize_paper_node(state: ResearchState) -> dict:
    """
    节点 1：根据论文标题和摘要生成技术总结。
    """

    llm = get_llm()
    # 提示词
    prompt = f"""
你是一名 AI 技术研究助理，请阅读下面的论文标题和摘要，并生成结构化总结。

论文标题：
{state["paper_title"]}

论文摘要：
{state["paper_abstract"]}

请输出：
1. 这篇论文要解决的问题
2. 核心方法
3. 关键技术点
4. 对 AI / Agent / 机器人方向的潜在价值

要求：
- 使用中文
- 不要泛泛而谈
- 尽量使用技术语言
- 重点关注求职项目价值
"""

    response = llm.invoke(prompt)

    # 这里返回的是 {"summary": response.content} 而不是返回完整 state
    # LangGraph 节点通常返回对 state 的部分更新，框架会把这些字段合并回全局 state。
    # 官方文档也强调，节点会发出对 State 的更新
    return {
        "summary": response.content,
    }