from pathlib import Path
import sys
import time


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.tools.llm_safe_call import safe_llm_invoke


def assert_success_case() -> None:
    result = safe_llm_invoke(
        llm=lambda prompt: f"fixed response: {prompt}",
        prompt="hello",
        node_name="test_success",
        timeout_seconds=1,
        max_retries=2,
        retry_backoff_seconds=0,
    )

    assert result["ok"] is True
    assert result["content"] == "fixed response: hello"
    assert result["attempts"] == 1
    assert result["error_type"] is None
    assert result["node_name"] == "test_success"


def assert_exception_case() -> None:
    def failing_llm(prompt: str) -> str:
        raise RuntimeError("generic failure")

    result = safe_llm_invoke(
        llm=failing_llm,
        prompt="hello",
        node_name="test_exception",
        timeout_seconds=1,
        max_retries=2,
        retry_backoff_seconds=0,
    )

    assert result["ok"] is False
    assert result["content"] == ""
    assert result["error_type"]
    assert result["attempts"] == 1
    assert result["node_name"] == "test_exception"


def assert_timeout_case() -> None:
    def slow_llm(prompt: str) -> str:
        time.sleep(0.05)
        return "late response"

    result = safe_llm_invoke(
        llm=slow_llm,
        prompt="hello",
        node_name="test_timeout",
        timeout_seconds=0.001,
        max_retries=0,
        retry_backoff_seconds=0,
    )

    assert result["ok"] is False
    assert result["content"] == ""
    assert result["error_type"] == "timeout"
    assert result["attempts"] == 1
    assert result["node_name"] == "test_timeout"


def assert_content_too_long_case() -> None:
    def too_long_llm(prompt: str) -> str:
        raise RuntimeError("context length exceeded: input too long")

    result = safe_llm_invoke(
        llm=too_long_llm,
        prompt="hello",
        node_name="test_content_too_long",
        timeout_seconds=1,
        max_retries=2,
        retry_backoff_seconds=0,
    )

    assert result["ok"] is False
    assert result["content"] == ""
    assert result["error_type"] == "content_too_long"
    assert result["attempts"] == 1
    assert result["node_name"] == "test_content_too_long"


def main() -> None:
    assert_success_case()
    print("success case passed")

    assert_exception_case()
    print("exception case passed")

    assert_timeout_case()
    print("timeout case passed")

    assert_content_too_long_case()
    print("content_too_long case passed")

    print("All safe_llm_invoke smoke tests passed.")


if __name__ == "__main__":
    main()
