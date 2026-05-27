# 文本切分模块
from dataclasses import dataclass
import re


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
    page_start: int | None = None
    page_end: int | None = None
    section_title: str | None = None


NOISE_KEYWORDS = (
    "arxiv:",
    "provided proper attribution",
    "google hereby grants permission",
    "reproduce the tables and figures",
    "solely for use",
    "journalistic or",
    "scholarly works",
    "copyright",
    "proceedings",
    "conference",
    "preprint",
    "submitted",
    "accepted",
)


SECTION_PATTERNS = (
    "Abstract",
    "Introduction",
    "Related Work",
    "Background",
    "Method",
    "Methods",
    "Methodology",
    "Approach",
    "Model",
    "Experiments",
    "Experimental Results",
    "Results",
    "Discussion",
    "Conclusion",
    "Conclusions",
    "References",
    "Appendix",
)


def _is_page_marker(line: str) -> bool:
    line = line.strip().lower()
    return line.startswith("[page") and line.endswith("]")


def _is_noise_line(line: str) -> bool:
    lower_line = line.strip().lower()

    if not lower_line:
        return True

    if _is_page_marker(line):
        return True

    return any(keyword in lower_line for keyword in NOISE_KEYWORDS)


def _clean_lines_for_page_mapping(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not _is_noise_line(line)
    ]


def _parse_raw_text_pages(raw_text: str) -> list[tuple[int, str]]:
    pages: list[tuple[int, str]] = []
    current_page: int | None = None
    current_lines: list[str] = []

    for line in raw_text.splitlines():
        marker_match = re.match(r"^\s*\[Page\s+(\d+)\]\s*$", line, flags=re.IGNORECASE)

        if marker_match:
            if current_page is not None:
                pages.append((current_page, "\n".join(current_lines)))

            current_page = int(marker_match.group(1))
            current_lines = []
            continue

        if current_page is not None:
            current_lines.append(line)

    if current_page is not None:
        pages.append((current_page, "\n".join(current_lines)))

    return pages


def build_page_spans_from_raw_text(
    raw_text: str,
    cleaned_text: str,
) -> list[dict[str, int]]:
    """
    Build page spans in cleaned_text coordinates from raw_text page markers.

    This is intentionally heuristic: it preserves the existing cleaned text and
    only maps page-local cleaned snippets back into that text.
    """

    if not raw_text or not cleaned_text:
        return []

    page_spans: list[dict[str, int]] = []
    search_start = 0

    for page_number, page_text in _parse_raw_text_pages(raw_text):
        page_cleaned = "\n".join(_clean_lines_for_page_mapping(page_text)).strip()

        if not page_cleaned:
            continue

        page_start = cleaned_text.find(page_cleaned, search_start)

        if page_start == -1:
            # Fall back to a shorter prefix, because global truncation may cut
            # the final page or PDF extraction can introduce small differences.
            page_prefix = page_cleaned[: min(300, len(page_cleaned))]
            page_start = cleaned_text.find(page_prefix, search_start)

        if page_start == -1:
            continue

        page_end = min(page_start + len(page_cleaned), len(cleaned_text))

        page_spans.append(
            {
                "page": page_number,
                "start_char": page_start,
                "end_char": page_end,
            }
        )

        search_start = page_end

    return page_spans


def infer_page_range(
    start_char: int,
    end_char: int,
    page_spans: list[dict[str, int]] | None,
) -> tuple[int | None, int | None]:
    if not page_spans:
        return None, None

    pages = []

    for span in page_spans:
        span_start = span["start_char"]
        span_end = span["end_char"]

        if span_start < end_char and span_end > start_char:
            pages.append(span["page"])

    if not pages:
        return None, None

    return min(pages), max(pages)


def _normalize_section_title(line: str) -> str | None:
    line = line.strip()
    line = re.sub(r"^\d+(\.\d+)*\.?\s+", "", line)
    line = re.sub(r"^[IVXLC]+\.\s+", "", line, flags=re.IGNORECASE)
    line = line.strip(":.- ").strip()

    for title in SECTION_PATTERNS:
        if line.lower() == title.lower():
            return title

    return None


def build_section_spans(text: str) -> list[dict[str, int | str]]:
    section_starts: list[dict[str, int | str]] = []
    offset = 0

    for line in text.splitlines():
        section_title = _normalize_section_title(line)

        if section_title is not None:
            section_starts.append(
                {
                    "section_title": section_title,
                    "start_char": offset,
                }
            )

        offset += len(line) + 1

    section_spans: list[dict[str, int | str]] = []

    for index, section in enumerate(section_starts):
        next_start = (
            int(section_starts[index + 1]["start_char"])
            if index + 1 < len(section_starts)
            else len(text)
        )
        section_spans.append(
            {
                "section_title": section["section_title"],
                "start_char": int(section["start_char"]),
                "end_char": next_start,
            }
        )

    return section_spans


def infer_section_title(
    start_char: int,
    section_spans: list[dict[str, int | str]] | None,
) -> str | None:
    if not section_spans:
        return None

    current_section: str | None = None

    for section in section_spans:
        if int(section["start_char"]) <= start_char < int(section["end_char"]):
            current_section = str(section["section_title"])
            break

    return current_section


def infer_section_title_from_chunk_text(chunk_text: str) -> str | None:
    for line in chunk_text.splitlines():
        section_title = _normalize_section_title(line)

        if section_title is not None:
            return section_title

    return None


def split_text_into_chunks(
    text: str,
    chunk_size: int = 800,
    chunk_overlap: int = 120,
    page_spans: list[dict[str, int]] | None = None,
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
    section_spans = build_section_spans(text)

    start = 0
    chunk_id = 0

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk_text = text[start:end].strip()

        if chunk_text:
            page_start, page_end = infer_page_range(
                start_char=start,
                end_char=end,
                page_spans=page_spans,
            )
            section_title = infer_section_title(
                start_char=start,
                section_spans=section_spans,
            )

            if section_title is None:
                section_title = infer_section_title_from_chunk_text(chunk_text)

            chunks.append(
                TextChunk(
                    chunk_id=chunk_id,
                    text=chunk_text,
                    start_char=start,
                    end_char=end,
                    page_start=page_start,
                    page_end=page_end,
                    section_title=section_title,
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
        print(f"Page: {chunk.page_start} - {chunk.page_end}")
        print(f"Section: {chunk.section_title}")
        # 仅展示每个 chunk 的前 300 个字符
        # print(chunk.text[:max_preview_chars])
        # print(chunk.text)
        print()
