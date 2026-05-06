# nodes/ 只放 LangGraph 节点 | 负责把 PDF 读取能力接入 LangGraph state
from app.states import PaperState
from app.tools.pdf_loader_pro import clean_paper_text, load_pdf_text, extract_paper_title


def load_pdf_node(state: PaperState) -> PaperState:
    """
    LangGraph node:
    Load PDF text and clean it.
    """
    pdf_path = state["pdf_path"]

    raw_text = load_pdf_text(pdf_path)
    paper_title = extract_paper_title(raw_text)
    paper_text = clean_paper_text(raw_text)

    return {
        **state,
        "paper_title": paper_title,
        "raw_text": raw_text,
        "paper_text": paper_text,
    }

# tools/pdf_loader.py：输入 pdf_path，输出 text
# nodes/load_pdf.py：输入 state，输出更新后的 state