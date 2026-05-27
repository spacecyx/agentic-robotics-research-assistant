from app.states import PaperState
from app.tools.text_splitter import build_page_spans_from_raw_text, split_text_into_chunks


def split_text_node(state: PaperState) -> dict:
    """
    Split cleaned paper text into searchable chunks.
    """
    print(">>> running split_text_node")
    
    # 读取 state 的(更新)字段
    paper_text = state.get("paper_text") or state.get("raw_text") or ""
    raw_text = state.get("raw_text", "")

    if not paper_text.strip():
        raise ValueError("No paper text found in state. Please check load_pdf_node output.")

    page_spans = build_page_spans_from_raw_text(
        raw_text=raw_text,
        cleaned_text=paper_text,
    )

    chunks = split_text_into_chunks(
        text=paper_text,
        chunk_size=1000,
        chunk_overlap=150,
        page_spans=page_spans,
    )

    # 在 LangGraph 里，node 的返回值不是这个节点的计算结果本身，而是对全局 State 的局部更新
    # 又 LangGraph 的状态是一个类似字典的对象，故每个节点执行完后，LangGraph 需要知道这次更新的是 state 里的哪个字段
    # 所以必须用字典明确指定字段名 | 这次切分出来的 chunks 写回到 State 的 chunks 字段里
    return {
        "chunks": chunks,
    }
