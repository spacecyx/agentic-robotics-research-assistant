from app.states import PaperState
from app.tools.llm_client import get_llm
from app.tools.llm_safe_call import classify_llm_error, safe_llm_invoke


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
    print(">>> running summarize_paper_node")
    
    prompt = SUMMARY_PROMPT.format(
        # paper_text=state["paper_text"]       # based on full text
        paper_text=state["retrieved_context"]  # based on retrieved chunks
    )

    node_name = "summarize_paper_node"
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
            "paper_summary": (
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
            "paper_summary": (
                f"[LLM generation failed in {node_name}: {result['error_type']}. "
                "Please check trace log for details.]"
            ),
            "errors": errors,
            "llm_invocations": llm_invocations,
        }

    return {
        **state,
        "paper_summary": result["content"],
        "errors": errors,
        "llm_invocations": llm_invocations,
    }
    # 这里返回的是 {"paper_summary": response.content} 而不是返回完整 state
    # LangGraph 节点通常返回对 state 的部分更新，框架会把这些字段合并回全局 state。
    # 官方文档也强调，节点会发出对 State 的更新
