from app.states import ResearchState
from app.tools.llm_client import get_llm

# 批判性分析节点
# 该节点体现的是多阶段工作流:先总结，再评价。这比一次性 prompt 更像真实 Agent 任务拆解

def critique_paper_node(state: ResearchState) -> dict:
    """
    节点 2：基于技术总结，进一步生成批判性分析。
    """

    llm = get_llm()

    prompt = f"""
你是一名严格的 AI / 机器人方向技术面试官。

下面是一篇论文的初步技术总结：

{state["summary"]}

请进一步分析：
1. 这个方法可能有什么局限？
2. 如果要复现，难点可能在哪里？
3. 如果作为求职项目，应该如何扩展？
4. 它和 AI Agent / LLM 应用工程岗位有什么关联？

要求：
- 中文输出
- 站在求职和项目展示角度分析
- 不要只说优点，也要指出风险
- 输出要结构化
"""

    response = llm.invoke(prompt)

    return {
        "critique": response.content,
    }