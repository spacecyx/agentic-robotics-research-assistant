# 评估 TF-IDF、Embedding 和 Hybrid Retriever 的检索效果
from pathlib import Path
import argparse
import json
from statistics import mean

from app.states import PaperState
from app.nodes.load_pdf import load_pdf_node
from app.nodes.split_text import split_text_node
from app.tools.retrievers.factory import create_retriever


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate TF-IDF, embedding and hybrid retrievers."
    )

    parser.add_argument(
        "--pdf",
        type=str,
        required=True,
        help="Path to the input paper PDF.",
    )

    parser.add_argument(
        "--eval-json",
        type=str,
        default="data/eval_queries.json",
        help="Path to the evaluation query JSON file.",
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of retrieved chunks.",
    )

    parser.add_argument(
        "--embedding-model",
        type=str,
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Embedding model name or local model path.",
    )

    parser.add_argument(
        "--alpha",
        type=float,
        default=0.6,
        help="Hybrid retrieval weight for embedding score.",
    )

    parser.add_argument(
        "--candidate-k",
        type=int,
        default=20,
        help="Number of candidates retrieved from each retriever before hybrid fusion.",
    )

    return parser.parse_args()


# 复用 load_pdf_node 和 split_text_node
def prepare_chunks(pdf_path: str):
    state: PaperState = {
        "pdf_path": pdf_path,
    }

    loaded_state = load_pdf_node(state)
    state.update(loaded_state)

    split_state = split_text_node(state)
    state.update(split_state)

    return state["chunks"]


def main() -> None:
    args = parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {args.pdf}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Input file must be a PDF: {args.pdf}")

    eval_json_path = Path(args.eval_json)
    if not eval_json_path.exists():
        raise FileNotFoundError(f"Eval JSON file not found: {args.eval_json}")

    with eval_json_path.open("r", encoding="utf-8") as f:
        eval_queries = json.load(f)

    chunks = prepare_chunks(str(pdf_path))

    retriever_configs = [
        {
            "name": "tfidf",
            "kwargs": {
                "retriever_type": "tfidf",
                "chunks": chunks,
            },
        },
        {
            "name": "embedding",
            "kwargs": {
                "retriever_type": "embedding",
                "chunks": chunks,
                "embedding_model": args.embedding_model,
            },
        },
        {
            "name": "hybrid",
            "kwargs": {
                "retriever_type": "hybrid",
                "chunks": chunks,
                "embedding_model": args.embedding_model,
                "alpha": args.alpha,
                "candidate_k": args.candidate_k,
            },
        },
    ]

    print(f"PDF: {pdf_path}")
    print(f"Eval JSON: {eval_json_path}")
    print(f"Number of chunks: {len(chunks)}")
    print(f"Number of eval queries: {len(eval_queries)}")
    print(f"Top-K: {args.top_k}")
    print(f"Alpha: {args.alpha}")
    print(f"Candidate-K: {args.candidate_k}")

    print("\n========== RETRIEVAL EVALUATION ==========\n")
    print(f"{'Retriever':<12} {'Hit@K':<10} {'MRR@K':<10} {'Avg Rank':<10}")
    print("-" * 46)

    for retriever_config in retriever_configs:
        retriever_name = retriever_config["name"]
        retriever = create_retriever(**retriever_config["kwargs"])

        hit_scores = []
        mrr_scores = []
        ranks = []

        for eval_item in eval_queries:
            query = eval_item["query"]
            expected_keywords = eval_item["expected_keywords"]
            min_keyword_matches = eval_item.get("min_keyword_matches", 1)

            retrieval_results = retriever.search(
                query=query,
                top_k=args.top_k,
            )

            first_hit_rank = None

            for rank, retrieval_result in enumerate(retrieval_results, start=1):
                chunk_text = retrieval_result.chunk.text.lower()

                matched_count = 0
                for keyword in expected_keywords:
                    if keyword.lower() in chunk_text:
                        matched_count += 1

                if matched_count >= min_keyword_matches:
                    first_hit_rank = rank
                    break

            if first_hit_rank is None:
                hit_scores.append(0.0)
                mrr_scores.append(0.0)
                ranks.append(args.top_k + 1)
            else:
                hit_scores.append(1.0)
                mrr_scores.append(1.0 / first_hit_rank)
                ranks.append(first_hit_rank)

        hit_at_k = mean(hit_scores)
        mrr_at_k = mean(mrr_scores)
        avg_rank = mean(ranks)

        print(
            f"{retriever_name:<12} "
            f"{hit_at_k:<10.3f} "
            f"{mrr_at_k:<10.3f} "
            f"{avg_rank:<10.3f}"
        )


if __name__ == "__main__":
    main()