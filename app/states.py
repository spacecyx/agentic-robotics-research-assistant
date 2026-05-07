from typing import TypedDict

# Day 4 import
from app.tools.text_splitter import TextChunk
from app.tools.simple_retriever import RetrievalResult

# 定义 Agent 工作流里所有节点共享的数据结构
# total=False:LangGraph 每个节点只返回自己更新的字段，不需要每个节点都补全所有字段
class PaperState(TypedDict, total=False):
    """
    State shared across the paper analysis workflow 
    LangGraph 中所有节点共享和更新的状态对象
    """

    # Input
    pdf_path: str
    query: str 

    # PDF processing
    raw_text: str
    paper_text: str
    paper_title: str

    # Chunking and retrieval
    chunks: list[TextChunk]
    retrieval_results: list[RetrievalResult]
    retrieved_context: str

    # LLM outputs
    paper_summary: str
    paper_critique: str

    # Final report
    final_report: str
    output_path: str