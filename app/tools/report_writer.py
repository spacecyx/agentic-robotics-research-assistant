# 报告保存
# 后续如果修改 JSON、HTML、PDF 输出，也不会污染 LangGraph 节点逻辑
from pathlib import Path
from datetime import datetime
import re


def sanitize_filename(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"[^a-zA-Z0-9_\-]+", "_", name)
    name = re.sub(r"_+", "_", name)
    return name.strip("_") or "paper"


def build_report_output_path(pdf_path: str, output_dir: str = "outputs") -> str:
    pdf_stem = Path(pdf_path).stem
    safe_stem = sanitize_filename(pdf_stem)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = Path(output_dir) / f"{safe_stem}_rag_report_{timestamp}.md"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    return str(output_path)


def save_markdown_report(report: str, output_path: str) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")
    return str(path)