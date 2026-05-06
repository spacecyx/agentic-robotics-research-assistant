import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


# 后续若需要切换模型 OpenAI/DeepSeek/Qwen
# 只需要改 .env，不用动业务代码
def get_llm() -> ChatOpenAI:
    """
    创建 OpenAI-compatible Chat 模型客户端。
    """
    
    load_dotenv()
    # default / example
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set. Please check your .env file.")

    return ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=0.2,
    )