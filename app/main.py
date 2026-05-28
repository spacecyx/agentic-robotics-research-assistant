from pathlib import Path
import argparse

from app.graph import build_graph
from app.states import PaperState


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Agentic Research Assistant for Robotics, SLAM, and 3D Perception Papers"
    )

    parser.add_argument(
        "--pdf",
        type=str,
        required=True,
        help="Path to the input paper PDF.",
    )

    parser.add_argument(
        "--query",
        type=str,
        default="What are the main problem, method, contribution, experimental results, and limitations of this paper?",
        help="Query used to retrieve relevant chunks from the paper.",
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of top retrieved chunks used as RAG context.",
    )

    # new add in Day 6
    # 选择 RAG 检索方式
    parser.add_argument(
        "--retriever-type",
        type=str,
        default="tfidf",
        choices=["tfidf", "embedding", "hybrid", "faiss"],
        help="Retriever type used for RAG context retrieval.",
    )

    # 选择 embedding 模型
    parser.add_argument(
        "--embedding-model",
        type=str,
        default="sentence-transformers/all-MiniLM-L6-v2", 
        help="Embedding model name used by embedding retriever.",
    )

    # plus work ~ faiss 
    parser.add_argument(
        "--faiss-index-dir",
        type=str,
        default="",
        help="Directory of FAISS index files. Default: data/index/<pdf_stem> when using faiss.",
    )

    parser.add_argument(
        "--rebuild-faiss-index",
        action="store_true",
        help="Rebuild FAISS index even if it already exists.",
    )

    # plus work multi-query
    parser.add_argument(
        "--use-query-expansion",
        action="store_true",
        help="Enable heuristic query expansion and multi-query retrieval.",
    )

    parser.add_argument(
        "--query-expansion-max-queries",
        type=int,
        default=4,
        help="Maximum number of query variants used in multi-query retrieval.",
    )

    parser.add_argument(
        "--multi-query-per-query-k",
        type=int,
        default=10,
        help="Number of chunks retrieved for each expanded query.",
    )

    parser.add_argument(
        "--multi-query-rrf-k",
        type=int,
        default=60,
        help="RRF constant used when merging multi-query retrieval results.",
    )

    parser.add_argument(
        "--reranker-type",
        type=str,
        default="score_fusion",
        choices=["keyword", "score_fusion", "section_prior", "robotics_tag_prior", "none"],
        help="Reranker type used after first-stage retrieval.",
    )

    parser.add_argument(
        "--retriever-weight",
        type=float,
        default=0.7,
        help="Weight of original retriever score in score-based rerankers.",
    )

    parser.add_argument(
        "--trace-dir",
        type=str,
        default="outputs/traces",
        help="Directory used to save lightweight workflow trace JSON files.",
    )

    parser.add_argument(
        "--disable-trace",
        action="store_true",
        help="Disable lightweight workflow trace JSON output.",
    )

    return parser.parse_args()


# validate pdf path
def validate_pdf_path(pdf_path: str) -> Path:
    path = Path(pdf_path)

    # path check
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # suffix check
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Input file must be a PDF: {pdf_path}")
    
    return path


# print retrieval results
def print_retrieval_results(result: PaperState) -> None:
    print("========== RETRIEVED CHUNKS ==========\n")

    retrieval_results = result.get("retrieval_results", [])

    if not retrieval_results:
        print("No retrieval results found.\n")
        return

    for rank, retrieval_result in enumerate(retrieval_results, start=1):
        chunk = retrieval_result.chunk
        score = retrieval_result.score

        print("=" * 100)
        print(f"Rank: {rank}")
        print(f"Chunk ID: {chunk.chunk_id}")
        print(f"Score: {score:.4f}")
        print(f"Char Range: {chunk.start_char} - {chunk.end_char}")
        print("-" * 100)
        print(chunk.text[:700])
        print()
    

def main() -> None:
    args = parse_args()
    pdf_path = validate_pdf_path(args.pdf)

    graph = build_graph()

    # FAISS 本地向量索引
    faiss_index_dir = (
        args.faiss_index_dir
        if args.faiss_index_dir
        else str(Path("data/index") / pdf_path.stem)
    )

    initial_state: PaperState = {
        "pdf_path": str(pdf_path),
        "query": args.query,
        "top_k": args.top_k,
        "retriever_type": args.retriever_type,
        "embedding_model": args.embedding_model,
        "faiss_index_dir": faiss_index_dir,
        "rebuild_faiss_index": args.rebuild_faiss_index,
        "use_query_expansion": args.use_query_expansion,
        "query_expansion_max_queries": args.query_expansion_max_queries,
        "multi_query_per_query_k": args.multi_query_per_query_k,
        "multi_query_rrf_k": args.multi_query_rrf_k,
        "reranker_type": args.reranker_type,
        "retriever_weight": args.retriever_weight,
        "trace_dir": args.trace_dir,
        "disable_trace": args.disable_trace,
    }

    # 展示选择的模型
    # print(f"Retriever type: {result.get('retriever_type', args.retriever_type)}")

    result = graph.invoke(initial_state)

    print("\n========== PAPER ANALYSIS FINISHED ==========\n")
    # print_retrieval_results(result)

    print("========== FINAL REPORT ==========\n")
    print(f"Report saved to: {result.get('output_path', '')}")
    if result.get("trace_path"):
        print(f"Trace saved to: {result.get('trace_path', '')}")


if __name__ == "__main__":
    main()
