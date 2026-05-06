from pathlib import Path

from pypdf import PdfReader

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


AFFILIATION_KEYWORDS = (
    "university",
    "institute",
    "research",
    "google brain",
    "google research",
    "microsoft research",
    "department",
    "school of",
    "laboratory",
)

# 文章载入
def load_pdf_text(pdf_path: str) -> str:
    """
    Load raw text from a PDF file.
    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Raw extracted text from all pages with page markers.
    """
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Input file is not a PDF: {pdf_path}")

    reader = PdfReader(str(path))

    # 创建一个名为 pages_text 的空列表 | 类型提示 (Type Hinting)：: list[str]
    pages_text: list[str] = []

    for page_idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        # 移除字符串开头和末尾的所有空白字符 (包括空格、制表符 \t、换行符 \n) | 不会处理str中的空格
        text = text.strip()

        if text:
            pages_text.append(f"\n\n[Page {page_idx + 1}]\n{text}")

    raw_text = "\n".join(pages_text).strip()

    if not raw_text:
        raise ValueError(f"No extractable text found in PDF: {pdf_path}")

    return raw_text

# [Page X] 判定
def is_page_marker(line: str) -> bool:
    """
    Check whether a line is a page marker like [Page 1].
    """
    # 首尾去空白字符 + 转小写 | 有点规范化/标准化的意思
    lower_line = line.strip().lower()
    return lower_line.startswith("[page") and lower_line.endswith("]")

# 干扰判定
def is_noise_line(line: str) -> bool:
    """
    Check whether a line is boilerplate noise.
    """
    lower_line = line.strip().lower()

    if not lower_line:
        return True

    if is_page_marker(line):
        return True

    return any(keyword in lower_line for keyword in NOISE_KEYWORDS)

# 清洗/规范化文章内容
def normalize_paper_lines(raw_text: str) -> list[str]:
    """
    Normalize raw paper text into cleaned, non-empty, non-noise lines.

    This is the shared preprocessing step used by both title extraction
    and paper text cleaning.
    """
    # 按行切分 | 把一整块长长的文本，变成一个由每一行字符串组成的列表
    lines = raw_text.splitlines()

    normalized_lines: list[str] = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if is_noise_line(line):
            continue

        normalized_lines.append(line)

    return normalized_lines

# 启发式/排除法 从清洗行中提取文章标题的工具函数 | 目前仅适用于英文文章
def extract_paper_title_from_lines(
    lines: list[str],
    fallback_title: str = "Unknown Paper",
) -> str:
    """
    Extract paper title from normalized paper lines.

    The title is usually located before the abstract and before author /
    affiliation information.
    """
    if not lines:
        return fallback_title

    title_search_lines: list[str] = []

    for line in lines[:100]:
        lower_line = line.lower()

        if lower_line == "abstract":
            break

        title_search_lines.append(line)

    if not title_search_lines:
        return fallback_title

    for line in title_search_lines[:40]:
        lower_line = line.lower()
        words = line.split()

        # Skip overly long lines.
        if len(words) > 20:
            continue

        # Must contain alphabetic characters.
        if not any(ch.isalpha() for ch in line):
            continue

        # Skip affiliation lines.
        if any(keyword in lower_line for keyword in AFFILIATION_KEYWORDS):
            continue

        # Skip likely author lines.
        author_markers = ("∗", "†", "‡")
        if any(marker in line for marker in author_markers):
            continue

        # Skip likely author lists.
        if line.count(",") >= 2:
            continue

        return line

    return fallback_title

# 提取文章标题
def extract_paper_title(
    raw_text: str,
    fallback_title: str = "Unknown Paper",
) -> str:
    """
    Extract paper title from raw paper text.

    This function reuses normalize_paper_lines(), so title extraction and
    paper cleaning share the same basic noise-removal logic.
    """
    lines = normalize_paper_lines(raw_text)
    return extract_paper_title_from_lines(
        lines=lines,
        fallback_title=fallback_title,
    )

# 清洗文本
def clean_paper_text(raw_text: str, max_chars: int = 30000) -> str:
    """
    Clean extracted paper text for LLM input.

    This function reuses normalize_paper_lines(), so it stays consistent
    with title extraction.
    """
    lines = normalize_paper_lines(raw_text)
    cleaned_text = "\n".join(lines)

    # 超字数在末尾加[TRUNCATED]
    if len(cleaned_text) > max_chars:
        cleaned_text = cleaned_text[:max_chars]
        cleaned_text += (
            "\n\n[TRUNCATED] "
            "Only the first part of the paper is used in this Day 2 prototype."
        )

    return cleaned_text

# 如果想进一步避免 normalize_paper_lines() 被调用两次，也可以在 load_pdf_node() 里只调用一次\
# 但从易读和稳定的角度考虑，还是先按照共享规则来做
