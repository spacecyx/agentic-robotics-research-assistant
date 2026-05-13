# 定义数据骨架 定义 RAG 系统每个阶段的输入/输出协议
from dataclasses import dataclass, field
from typing import Any

@dataclass
class RetrievalResult:
    chunk: Any
    # chunks: list[TextChunk] # from app.tools.text_splitter import TextChunk
    score: float
    # new add in Day 7
    source: str = ""
    # 定义一个名为 metadata 的属性
    # 它是一个键为字符串、值为任意类型的字典，且每个新对象在创建时都能获得一个独立的空字典作为默认值
    metadata: dict[str, Any] = field(default_factory=dict)

