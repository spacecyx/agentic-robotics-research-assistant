# 定义数据骨架 定义 RAG 系统每个阶段的输入/输出协议
from dataclasses import dataclass
from typing import Any

@dataclass
class RetrievalResult:
    chunk: Any
    # chunks: list[TextChunk] # from app.tools.text_splitter import TextChunk
    score: float