"""
Lightweight safe wrapper for LLM calls.

This module is intentionally independent from existing LangGraph nodes so it
can be adopted incrementally without changing current workflow behavior.
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from typing import Any, Callable


RETRYABLE_ERROR_TYPES = {
    "timeout",
    "rate_limit",
    "network_error",
    "api_error",
}


def classify_llm_error(error: BaseException) -> str:
    """
    Classify common LLM/API errors without depending on provider-specific SDKs.
    """

    error_name = error.__class__.__name__.lower()
    error_message = str(error).lower()
    combined = f"{error_name} {error_message}"

    if isinstance(error, FutureTimeoutError) or "timeout" in combined or "timed out" in combined:
        return "timeout"

    if "rate limit" in combined or "ratelimit" in combined or "too many requests" in combined or "429" in combined:
        return "rate_limit"

    if (
        "connection" in combined
        or "network" in combined
        or "connecterror" in combined
        or "readerror" in combined
        or "dns" in combined
        or "socks" in combined
    ):
        return "network_error"

    if (
        "context length" in combined
        or "maximum context" in combined
        or "token limit" in combined
        or "too long" in combined
        or "max tokens" in combined
    ):
        return "content_too_long"

    if "api" in combined or "openai" in combined or "badrequest" in combined or "server" in combined:
        return "api_error"

    return "unknown_error"


def _invoke_model(
    llm_or_callable: Any,
    model_input: Any,
) -> Any:
    if callable(llm_or_callable) and not hasattr(llm_or_callable, "invoke"):
        return llm_or_callable(model_input)

    if hasattr(llm_or_callable, "invoke"):
        return llm_or_callable.invoke(model_input)

    raise TypeError("llm must be a callable or an object with an invoke method.")


def _extract_content(response: Any) -> str:
    if hasattr(response, "content"):
        return str(response.content)

    return str(response)


def safe_llm_invoke(
    llm: Any | Callable[[Any], Any],
    prompt: str | None = None,
    messages: list[Any] | None = None,
    node_name: str = "unknown",
    timeout_seconds: float = 60,
    max_retries: int = 2,
    retry_backoff_seconds: float = 1.0,
) -> dict[str, Any]:
    """
    Invoke an LLM or callable with timeout, retry, error classification, and latency stats.

    ``max_retries`` means retries after the first attempt. The returned
    ``attempts`` field is the actual number of attempts performed.
    """

    if prompt is None and messages is None:
        return {
            "ok": False,
            "content": "",
            "error_type": "unknown_error",
            "error_message": "Either prompt or messages must be provided.",
            "attempts": 0,
            "latency_ms": 0.0,
            "node_name": node_name,
        }

    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be greater than 0.")

    if max_retries < 0:
        raise ValueError("max_retries must be greater than or equal to 0.")

    if retry_backoff_seconds < 0:
        raise ValueError("retry_backoff_seconds must be greater than or equal to 0.")

    model_input = messages if messages is not None else prompt
    total_attempts = max_retries + 1
    start_time = time.perf_counter()
    last_error_type: str | None = None
    last_error_message: str | None = None

    for attempt in range(1, total_attempts + 1):
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(_invoke_model, llm, model_input)

        try:
            response = future.result(timeout=timeout_seconds)
            executor.shutdown(wait=False, cancel_futures=True)
            latency_ms = (time.perf_counter() - start_time) * 1000.0

            return {
                "ok": True,
                "content": _extract_content(response),
                "error_type": None,
                "error_message": None,
                "attempts": attempt,
                "latency_ms": latency_ms,
                "node_name": node_name,
            }
        except FutureTimeoutError as error:
            future.cancel()
            executor.shutdown(wait=False, cancel_futures=True)
            last_error_type = classify_llm_error(error)
            last_error_message = f"LLM call timed out after {timeout_seconds} seconds."
        except Exception as error:
            executor.shutdown(wait=False, cancel_futures=True)
            last_error_type = classify_llm_error(error)
            last_error_message = str(error)

        should_retry = (
            last_error_type in RETRYABLE_ERROR_TYPES
            and attempt < total_attempts
        )

        if not should_retry:
            break

        if retry_backoff_seconds > 0:
            time.sleep(retry_backoff_seconds * attempt)

    latency_ms = (time.perf_counter() - start_time) * 1000.0

    return {
        "ok": False,
        "content": "",
        "error_type": last_error_type or "unknown_error",
        "error_message": last_error_message or "Unknown LLM invocation error.",
        "attempts": attempt,
        "latency_ms": latency_ms,
        "node_name": node_name,
    }
