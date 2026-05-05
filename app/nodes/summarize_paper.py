from app.states import PaperState
from app.tools.llm_client import get_llm


SUMMARY_PROMPT = """
你是一个技术研究助理，正在帮助一名激光SLAM / 三维感知背景的工程师阅读深度学习论文。

请根据下面的论文内容，生成结构化摘要。

要求：
1. 使用中文回答。
2. 不要泛泛而谈，要聚焦技术问题、核心方法和工程意义。
3. 如果论文内容被截断，请明确说明。
4. 优先关注这篇论文对机器人、三维感知、大模型、多模态或 Agent 系统的潜在价值。
5. 不要编造论文中没有的信息。

输出格式：

## 论文摘要

### 1. 论文主题
用 2-3 句话说明这篇论文主要研究什么。

### 2. 研究问题
说明作者要解决什么核心问题。

### 3. 核心方法
分点说明关键模块、关键设计或核心机制。

### 4. 关键贡献
列出 3-5 点。

### 5. 重要技术细节
说明这篇论文中值得工程实现时关注的技术点。

### 6. 和机器人 / 3D 感知 / Agent 的关系
分别说明：
- 对机器人 / 3D 感知的价值：
- 对大模型 / 多模态的价值：
- 对 大模型 / 多模态 / Agent 系统的间接价值：

论文内容如下：

{paper_text}
"""


def summarize_paper_node(state: PaperState) -> PaperState:
    """
    LangGraph node:
    Generate a structured paper summary.
    """
    llm = get_llm()

    prompt = SUMMARY_PROMPT.format(
        paper_text=state["paper_text"]
    )

    response = llm.invoke(prompt)

    return {
        **state,
        "paper_summary": response.content,
    }
    # 这里返回的是 {"paper_summary": response.content} 而不是返回完整 state
    # LangGraph 节点通常返回对 state 的部分更新，框架会把这些字段合并回全局 state。
    # 官方文档也强调，节点会发出对 State 的更新