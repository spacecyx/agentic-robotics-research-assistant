# 给所有 retriever 一个统一接口
from typing import Protocol

from app.tools.retrievers.schemas import RetrievalResult


# 定义了一个协议 Protocol:任意对象，只要它拥有一个叫做 search 的方法，并且参数和返回值对得上，那它就是一个 BaseRetriever
class BaseRetriever(Protocol):
    # 方法名：必须叫 search；输入：必须接受一个字符串 query 和一个整数 top_k；输出：必须返回一个 RetrievalResult 对象的列表
    def search(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        # ... 代表这里不需要实现具体逻辑 | 占位符
        ...
    # 后续不管是 TF-IDF、Embedding、BM25、Hybrid、Reranker，都可以遵循这个接口