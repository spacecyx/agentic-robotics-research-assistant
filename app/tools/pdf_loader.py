# tools/ 只放底层工具能力 | 负责 PDF 读取和清洗
from pathlib import Path
from pypdf import PdfReader

# PDF 文件 → 原始文本
# 原始文本 → 初步清洗后的论文文本
# 获取文章题目


# 如何读取？
def load_pdf_text(pdf_path: str) -> str:
    """
    Load raw text from a PDF file.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Raw extracted text from all pages.
    """
    # 用 pathlib.Path 对象来处理路径
    path = Path(pdf_path, strict=False) # 提高对非标准 PDF 格式的兼容性

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    # 后缀名检查 | 防止意外读取图片或二进制文件
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Input file is not a PDF: {pdf_path}")

    # 初始化 PDF 阅读器
    reader = PdfReader(str(path))

    pages_text: list[str] = []

    # 循环访问 PDF 的每一页
    for page_idx, page in enumerate(reader.pages):
        text = page.extract_text() or "" # 空页面鲁棒
        text = text.strip()

        if text:
            # 先对每一页正常文本 加上 [Page X] 的标签
            # 再将每页内容暂存入列表
            pages_text.append(f"\n\n[Page {page_idx + 1}]\n{text}") 
    # 将所有页面内容合并为一个大字符串，并在页面之间插入换行符"\n"
    raw_text = "\n".join(pages_text).strip()

    # 如果合并后的 raw_text 依然为空，抛出 ValueError | 若 PDF 是扫描件, extract_text() 往往无法识别出文字, 该情况下会抛错
    if not raw_text:
        raise ValueError(f"No extractable text found in PDF: {pdf_path}")

    return raw_text

# 排除法 提取 paper 题目 | 启发式的 没上LLM 目前够用 | 该版本是基于英文论文考虑的
# 从论文的前几十行文字中筛选出最像标题的那一行 
def extract_paper_title(text: str, fallback_title: str = "Unknown Paper") -> str:
    """
    Extract paper title from the beginning of the paper text.

    Day 2 heuristic:
    1. Remove page markers such as [Page 1].
    2. Skip copyright / arXiv / conference boilerplate.
    3. Search before Abstract when possible.
    4. Return the first title-like line.
    """
    # 分行清洗
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    if not lines:
        return fallback_title # "Unknown Paper"

    # 定义背景噪音
    noise_keywords = (
        "[page",
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

    candidate_lines: list[str] = []

    for line in lines[:100]:
        lower_line = line.lower()

        # Skip page markers and boilerplate.
        if any(keyword in lower_line for keyword in noise_keywords):
            continue

        # Stop at Abstract. The title should usually appear before Abstract.
        if lower_line == "abstract":
            break

        # Skip obvious emails.
        if "@" in line:
            continue

        # Skip very short fragments.
        if len(line) < 6:
            continue

        candidate_lines.append(line)

    if not candidate_lines:
        return fallback_title

    affiliation_keywords = (
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

    for line in candidate_lines[:40]:
        lower_line = line.lower()
        words = line.split()

        # Skip overly long lines.
        if len(words) > 20:
            continue

        # Must contain alphabetic characters.
        if not any(ch.isalpha() for ch in line):
            continue

        # Skip affiliation lines.
        if any(keyword in lower_line for keyword in affiliation_keywords):
            continue

        # Skip likely author lines.
        # Example: "Ashish Vaswani∗ Google Brain"
        author_markers = ("∗", "†", "‡")
        if any(marker in line for marker in author_markers):
            continue

        # Skip lines with many commas, often author lists.
        if line.count(",") >= 2:
            continue

        return line

    return fallback_title

# 如何清洗 | 压缩冗余信息：既能节省 Token（费用），又能避免无意义的空格干扰
def clean_paper_text(raw_text: str, max_chars: int = 30000) -> str:
    """
    Lightly clean extracted paper text.

    This is a Day 2 prototype:
    - remove excessive blank lines
    - keep page markers | 语境保留 
    - limit max characters for LLM context

    Args:
        raw_text: Raw text extracted from PDF.
        max_chars: Maximum number of characters to keep.

    Returns:
        Cleaned paper text.
    """
    lines = raw_text.splitlines()

    cleaned_lines: list[str] = []

    for line in lines:
        # 边缘清理 | 移除了每一行首尾的空格或制表符
        line = line.strip()

        # 去除冗余空行
        if not line:
            continue

        cleaned_lines.append(line)

    cleaned_text = "\n".join(cleaned_lines)

    # 截断机制:默认设为 30,000 字（大约对应 20k-40k 的 Token）
    if len(cleaned_text) > max_chars:
        cleaned_text = cleaned_text[:max_chars]
        # 发生截断 会在文章内容末尾加上[TRUNCATED]
        cleaned_text += (
            "\n\n[TRUNCATED] "
            "Only the first part of the paper is used in this Day 2 prototype."
        )

    return cleaned_text