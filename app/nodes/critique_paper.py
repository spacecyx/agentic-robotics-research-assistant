# 批判性分析节点
# 该节点体现的是多阶段工作流:先总结，再评价。这比一次性 prompt 更像真实 Agent 任务拆解

from app.states import PaperState
from app.tools.llm_client import get_llm
from app.tools.llm_safe_call import classify_llm_error, safe_llm_invoke


CRITIQUE_PROMPT = """
你是一个严谨的 AI 学习教练、求职策略顾问和技术研究助理。

下面请根据根据检索到的论文内容和文章总结，从求职和项目实践角度，对这篇论文进行批判性分析。

分析对象是一名有激光SLAM / 三维感知 / 机器人背景，正在转向深度学习 / 大模型 / Agent 方向的工程师。

请重点回答：
1. 这篇论文最值得掌握的思想是什么？
2. 对机器人 / 三维感知方向有什么实际价值？
3. 对大模型 / 多模态 / Agent 方向有什么间接价值？
4. 当前阶段是否值得深入学习？
5. 如果要把这篇论文的思想转化为项目亮点，可以怎么做？
6. 这篇论文有哪些局限，不能过度包装成什么？

输出格式：

## 论文批判性分析

### 1. 必须掌握的内容
列出真正必须掌握的点。

### 2. 建议掌握的内容
列出有价值但不是当前最优先的点。

### 3. 可以暂缓的内容
列出现在可以不深挖的内容。

### 4. 对机器人 / 3D 感知的价值
从感知模型、backbone、特征提取、表征学习等角度分析。

### 5. 对大模型 / 多模态 / Agent 的价值
从大模型基础、多模态建模、Agent 系统工程等角度分析。

### 6. 项目转化建议
说明如何把这篇论文里的思想转化为你的 Research Assistant 或机器人感知项目亮点。

### 7. 求职表达建议
给出可以写进简历或面试表达的说法。

### 8. 风险和局限
指出不能夸大的地方。

检索的论文内容如下：
{retrieved_context}

论文摘要如下：
{paper_summary}

"""


def critique_paper_node(state: PaperState) -> PaperState:
    """
    LangGraph node:
    Critique the paper from learning, project, and job-search perspectives.
    """
    print(">>> running critique_paper_node")
    
    prompt = CRITIQUE_PROMPT.format(
        retrieved_context=state["retrieved_context"], 
        paper_summary=state["paper_summary"]
    )

    node_name = "critique_paper_node"
    errors = list(state.get("errors", []))
    llm_invocations = list(state.get("llm_invocations", []))
    timeout_seconds = state.get("llm_timeout_seconds", 60)
    max_retries = state.get("llm_max_retries", 2)
    retry_backoff_seconds = state.get("llm_retry_backoff_seconds", 1.0)

    try:
        llm = get_llm()
    except Exception as error:
        error_type = classify_llm_error(error)
        error_record = {
            "node_name": node_name,
            "error_type": error_type,
            "error_message": str(error),
            "attempts": 0,
            "latency_ms": 0.0,
        }
        errors.append(error_record)
        llm_invocations.append(
            {
                "node_name": node_name,
                "ok": False,
                "error_type": error_type,
                "error_message": str(error),
                "attempts": 0,
                "latency_ms": 0.0,
                "timeout_seconds": timeout_seconds,
                "max_retries": max_retries,
                "fallback_used": True,
            }
        )

        return {
            **state,
            "paper_critique": (
                f"[LLM generation failed in {node_name}: {error_type}. "
                "Please check trace log for details.]"
            ),
            "errors": errors,
            "llm_invocations": llm_invocations,
        }

    result = safe_llm_invoke(
        llm=llm,
        prompt=prompt,
        node_name=node_name,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        retry_backoff_seconds=retry_backoff_seconds,
    )
    llm_invocations.append(
        {
            "node_name": result["node_name"],
            "ok": result["ok"],
            "error_type": result["error_type"],
            "error_message": result["error_message"],
            "attempts": result["attempts"],
            "latency_ms": result["latency_ms"],
            "timeout_seconds": timeout_seconds,
            "max_retries": max_retries,
            "fallback_used": not result["ok"],
        }
    )

    if not result["ok"]:
        errors.append(
            {
                "node_name": result["node_name"],
                "error_type": result["error_type"],
                "error_message": result["error_message"],
                "attempts": result["attempts"],
                "latency_ms": result["latency_ms"],
            }
        )

        return {
            **state,
            "paper_critique": (
                f"[LLM generation failed in {node_name}: {result['error_type']}. "
                "Please check trace log for details.]"
            ),
            "errors": errors,
            "llm_invocations": llm_invocations,
        }

    return {
        **state,
        "paper_critique": result["content"],
        "errors": errors,
        "llm_invocations": llm_invocations,
    }
