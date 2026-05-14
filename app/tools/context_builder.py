# Context Builder
# 作用：把检索/重排后的 RetrievalResult 转换为 LLM 可用的上下文

from dataclasses import dataclass
from typing import Any

from app.tools.retrievers.schemas import RetrievalResult
from app.tools.rerankers.base import get_chunk_text


@dataclass
class Evidence:
    """
    记录每个上下文片段的来源信息。

    后续 AnswerGenerator 可以基于这些信息输出 citation。
    """

    source_id: int
    chunk_id: int | None
    score: float
    source: str
    rank: int | None
    start_char: int | None
    end_char: int | None


@dataclass
class BuiltContext:
    """
    ContextBuilder 的输出结果。

    context:
        拼接后的上下文字符串，直接喂给 LLM。

    evidences:
        每个 Source 对应的结构化来源信息。
    """

    context: str
    evidences: list[Evidence]


class ContextBuilder:
    """
    将 RetrievalResult 构造成 LLM 输入上下文。

    主要职责：
    1. 按检索/重排顺序拼接 chunk
    2. 控制最大上下文长度 | 防止上下文太长 / 防止单个片段太长
    3. 去重
    4. 保留 chunk_id、score、rank 等 evidence 信息
    """

    def __init__(
        self,
        max_context_chars: int = 3000,  
        max_chunk_chars: int = 1000,        
    ):
        if max_context_chars <= 0:
            raise ValueError("max_context_chars must be positive.")

        if max_chunk_chars <= 0:
            raise ValueError("max_chunk_chars must be positive.")

        self.max_context_chars = max_context_chars
        self.max_chunk_chars = max_chunk_chars

    def build(
        self,
        results: list[RetrievalResult],
        max_results: int = 5,
    ) -> BuiltContext:
        if not results:
            return BuiltContext(
                context="",
                evidences=[],
            )

        max_results = max(1, min(max_results, len(results)))

        blocks: list[str] = []
        evidences: list[Evidence] = []

        used_chunk_keys: set[Any] = set()
        current_chars = 0
        source_id = 1

        for result in results:
            if len(evidences) >= max_results:
                break

            chunk = result.chunk
            chunk_text = get_chunk_text(result).strip()

            if not chunk_text:
                continue
            
            # 去重
            chunk_key = self._get_chunk_key(chunk)

            if chunk_key in used_chunk_keys:
                continue

            used_chunk_keys.add(chunk_key)

            chunk_id = getattr(chunk, "chunk_id", None)
            start_char = getattr(chunk, "start_char", None)
            end_char = getattr(chunk, "end_char", None)
            rank = result.metadata.get("rank")

            # 截断 (单块文本长度)
            if len(chunk_text) > self.max_chunk_chars:
                chunk_text = chunk_text[: self.max_chunk_chars].rstrip() + "..."

            # 格式化 (添加 Header)
            header = (
                f"[Source {source_id} | "
                f"chunk_id={chunk_id} | "
                f"score={result.score:.4f} | "
                f"rank={rank} | "
                f"source={result.source}]"
            )

            block = f"{header}\n{chunk_text}"

            remaining_chars = self.max_context_chars - current_chars

            if remaining_chars <= 0:
                break

            if len(block) > remaining_chars:
                # 剩余空间太少时，直接停止，避免构造过短的无效 context
                if remaining_chars < 200:
                    break

                allowed_text_chars = max(
                    0,
                    remaining_chars - len(header) - 10,
                )
                chunk_text = chunk_text[:allowed_text_chars].rstrip() + "..."
                block = f"{header}\n{chunk_text}"

            blocks.append(block)
            current_chars += len(block) + 2

            evidences.append(
                Evidence(
                    source_id=source_id,
                    chunk_id=chunk_id,
                    score=float(result.score),
                    source=result.source,
                    rank=rank,
                    start_char=start_char,
                    end_char=end_char,
                )
            )

            source_id += 1

        context = "\n\n".join(blocks)

        return BuiltContext(
            context=context,
            evidences=evidences,
        )


    # 服务用户
    def build_evidence_markdown(self, evidences: list[Evidence]) -> str:
        """
        将 evidence 信息转换成 Markdown，方便最终回答展示。
        """

        if not evidences:
            return "No evidence found."

        lines = []

        for evidence in evidences:
            lines.append(
                f"[{evidence.source_id}] "
                f"chunk_id={evidence.chunk_id}, "
                f"score={evidence.score:.4f}, "
                f"rank={evidence.rank}, "
                f"source={evidence.source}, "
                f"char_range=({evidence.start_char}, {evidence.end_char})"
            )

        return "\n".join(lines)

    @staticmethod
    def _get_chunk_key(chunk: Any) -> Any:
        """
        用于 chunk 去重。

        当前 TextChunk 有 chunk_id，可以优先使用 chunk_id。
        如果以后换成其他 chunk 类型，则退化为 id(chunk)。
        """

        if hasattr(chunk, "chunk_id"):
            return getattr(chunk, "chunk_id")

        return id(chunk)