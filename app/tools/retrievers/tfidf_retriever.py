# 原来 TF-IDF 检索逻辑的模块化版本
# 找字面上长得像的内容 | 不理解语义

from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.tools.retrievers.schemas import RetrievalResult

# BaseRetriever 协议的具体实现 ~ TF-IDF
class TfidfRetriever:
    def __init__(self, chunks: list[Any]):
        if not chunks:
            raise ValueError("TfidfRetriever requires a non-empty chunk list.")

        # 把所有的 chunks（文本块）拿出来
        self.chunks = chunks
        self.texts = [chunk.text for chunk in chunks]

        # 用 TfidfVectorizer 统计词频和逆文档频率
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
        )
        self.chunk_matrix = self.vectorizer.fit_transform(self.texts)

    # 必有一个 search 方法 输入输出满足要求
    def search(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        if not query.strip():
            raise ValueError("Query must not be empty.")

        top_k = max(1, min(top_k, len(self.chunks)))

        # 把用户的 query 也转化成一个 TF-IDF 向量
        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.chunk_matrix).flatten()

        # argsort()[::-1] 按照分数从高到低排个序，取前 top_k 个
        top_indices = scores.argsort()[::-1][:top_k]

        # 遍历 top_indices（通常是检索得分最高的前几个索引），并针对每一个索引创建一个 RetrievalResult 对象
        # 比起传统的 for 循环（先建空列表再 append），这种写法更加紧凑且执行效率更高
        # return [
        #     RetrievalResult(
        #         chunk=self.chunks[index],
        #         score=float(scores[index]),
        #     )
        #     for index in top_indices
        # ]
        # fixed in Day 7
        return [
            RetrievalResult(
                chunk=self.chunks[index],
                score=float(scores[index]),
                source="tfidf",
                metadata={
                    "chunk_index": int(index),
                    "tfidf_score": float(scores[index]),
                    "rank": rank + 1,
                },
            )
            for rank, index in enumerate(top_indices)
        ]