# 文本切分模块
from dataclasses import dataclass


@dataclass
class TextChunk:
    """
    A text chunk split from the original paper text.

    Attributes:
        chunk_id: The index of the chunk.
        text: The chunk content.
        start_char: Start character position in the original text.
        end_char: End character position in the original text.
    """

    chunk_id: int
    text: str
    start_char: int
    end_char: int


def split_text_into_chunks(
    text: str,
    chunk_size: int = 800,
    chunk_overlap: int = 120,
) -> list[TextChunk]:
    """
    Split long paper text into overlapping chunks.

    Args:
        text: Cleaned paper text.
        chunk_size: Maximum number of characters in each chunk.
        chunk_overlap: Number of overlapping characters between adjacent chunks.

    Returns:
        A list of TextChunk objects.
    """

    if not text or not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive.")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be non-negative.")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size.")

    chunks: list[TextChunk] = []

    text = text.strip()
    text_length = len(text)

    start = 0
    chunk_id = 0

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append(
                TextChunk(
                    chunk_id=chunk_id,
                    text=chunk_text,
                    start_char=start,
                    end_char=end,
                )
            )
            chunk_id += 1

        if end >= text_length:
            break

        start = end - chunk_overlap

    return chunks


def preview_chunks(chunks: list[TextChunk], max_preview_chars: int = 300) -> None:
    """
    Print a simple preview of chunks for manual inspection.
    """

    print(f"Total chunks: {len(chunks)}")

    for chunk in chunks[:3]:
        print("=" * 80)
        print(f"Chunk ID: {chunk.chunk_id}")
        print(f"Start: {chunk.start_char}, End: {chunk.end_char}")
        # 仅展示每个 chunk 的前 300 个字符
        # print(chunk.text[:max_preview_chars])
        # print(chunk.text)
        print()