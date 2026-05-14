# Answer Generator
# 作用：基于检索上下文生成带证据引用的回答

from dataclasses import dataclass

from app.tools.llm_client import get_llm


ANSWER_PROMPT = """
你是一个严谨的论文问答助手，正在帮助一名激光SLAM / 三维感知 / 机器人背景的工程师阅读深度学习论文。

请只根据给定的 Context 回答用户问题，不要编造 Context 中没有的信息。

要求：
1. 使用中文回答。
2. 回答要直接针对用户问题，不要泛泛总结全文。
3. 如果 Context 中证据不足，请明确说明“当前检索上下文不足以回答该问题”。
4. 回答中尽量引用来源编号，例如：[Source 1]、[Source 2]。
5. 不要输出 Evidence 列表，Evidence 会由系统在回答后自动附加。
6. 重点解释技术原因、工程意义和面试表达价值。

Paper Title:
{paper_title}

User Question:
{query}

Context:
{context}

请按以下格式输出：

## Answer

你的回答内容。
"""


@dataclass
class AnswerResult:
    """
    AnswerGenerator 的输出结果。

    answer:
        LLM 生成的回答正文。

    evidence_markdown:
        ContextBuilder 生成的 evidence 信息。

    final_markdown:
        最终可展示/保存的完整 Markdown。
    """

    answer: str
    evidence_markdown: str
    final_markdown: str


class AnswerGenerator:
    """
    基于检索上下文生成回答。

    注意：
    1. 不负责检索
    2. 不负责重排
    3. 不负责构造 context
    4. 只负责调用 LLM 生成 grounded answer
    """

    def __init__(self, paper_title: str = "Unknown Paper"):
        self.paper_title = paper_title

    def generate(
        self,
        query: str,
        context: str,
        evidence_markdown: str,
    ) -> AnswerResult:
        # query/context空检查
        if not query.strip():
            raise ValueError("Query must not be empty.")

        if not context.strip():
            answer = (
                "## Answer\n\n"
                "当前检索上下文为空，无法基于论文证据回答该问题。"
            )

            final_markdown = f"""{answer}

## Evidence

{evidence_markdown}
"""

            return AnswerResult(
                answer=answer,
                evidence_markdown=evidence_markdown,
                final_markdown=final_markdown,
            )

        llm = get_llm()

        prompt = ANSWER_PROMPT.format(
            paper_title=self.paper_title,
            query=query,
            context=context,
        )

        response = llm.invoke(prompt)
        answer = response.content.strip()

        final_markdown = f"""{answer}

## Evidence

{evidence_markdown}
"""

        return AnswerResult(
            answer=answer,
            evidence_markdown=evidence_markdown,
            final_markdown=final_markdown,
        )