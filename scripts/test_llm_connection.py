import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

response = client.chat.completions.create(
    model=os.getenv("OPENAI_MODEL"),
    messages=[
        {"role": "user", "content": "请用一句话介绍你自己"}
    ],
)

print(response.choices[0].message.content)


# 项目根目录下运行测试代码：python -m scripts.test_llm_connection