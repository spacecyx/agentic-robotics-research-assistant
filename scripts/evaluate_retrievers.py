# 评估 TF-IDF、Embedding、Hybrid 以及 Rerank 后的检索效果
from pathlib import Path
import argparse
import csv
import json
import unicodedata
from statistics import mean
from typing import Any

from app.states import PaperState
from app.nodes.load_pdf import load_pdf_node
from app.nodes.split_text import split_text_node
from app.tools.retrievers.factory import create_retriever
from app.tools.rerankers.factory import create_reranker


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate retrievers and reranked retrievers with weak keyword-based metrics."
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
        default=5,
        help="Final number of retrieved chunks used for evaluation.",
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
        help="Candidate number used inside HybridRetriever.",
    )

    parser.add_argument(
        "--rerank-candidate-k",
        type=int,
        default=15,
        help="Number of first-stage candidates passed to reranker.",
    )

    parser.add_argument(
        "--retriever-weight",
        type=float,
        default=0.7,
        help="Weight of original retriever score in score_fusion reranker.",
    )

    parser.add_argument(
        "--output-csv",
        type=str,
        default="",
        help="Optional path to save evaluation summary as CSV.",
    )

    parser.add_argument(
        "--show-details",
        action="store_true",
        help="Print per-query evaluation details.",
    )

    return parser.parse_args()


def prepare_chunks(pdf_path: str):
    state: PaperState = {
        "pdf_path": pdf_path,
    }

    loaded_state = load_pdf_node(state)
    state.update(loaded_state)

    split_state = split_text_node(state)
    state.update(split_state)

    return state["chunks"]


def normalize_text(text: str) -> str:
    """
    归一化文本，降低 PDF 抽取符号差异对 keyword matching 的影响。
    """

    text = unicodedata.normalize("NFKC", text)
    text = text.lower()

    replacements = {
        "×": "x",
        "−": "-",
        "–": "-",
        "—": "-",
        "ﬁ": "fi",
        "ﬂ": "fl",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def count_keyword_matches(chunk_text: str, expected_keywords: list[str]) -> int:
    normalized_chunk_text = normalize_text(chunk_text)

    matched_count = 0

    for keyword in expected_keywords:
        normalized_keyword = normalize_text(keyword)

        if normalized_keyword in normalized_chunk_text:
            matched_count += 1

    return matched_count


def find_first_hit_rank(
    retrieval_results: list[Any],
    expected_keywords: list[str],
    min_keyword_matches: int,
) -> int | None:
    for rank, retrieval_result in enumerate(retrieval_results, start=1):
        chunk_text = retrieval_result.chunk.text
        matched_count = count_keyword_matches(
            chunk_text=chunk_text,
            expected_keywords=expected_keywords,
        )

        if matched_count >= min_keyword_matches:
            return rank

    return None


def hit_at_rank(first_hit_rank: int | None, k: int) -> float:
    if first_hit_rank is None:
        return 0.0

    return 1.0 if first_hit_rank <= k else 0.0


def evaluate_method(
    method_name: str,
    retriever,
    eval_queries: list[dict[str, Any]],
    top_k: int,
    reranker=None,
    rerank_candidate_k: int = 15,
    show_details: bool = False,
) -> dict[str, Any]:
    hit_1_scores = []
    hit_3_scores = []
    hit_k_scores = []
    mrr_scores = []
    ranks = []

    first_stage_k = max(top_k, rerank_candidate_k)

    for eval_index, eval_item in enumerate(eval_queries, start=1):
        query = eval_item["query"]
        expected_keywords = eval_item["expected_keywords"]
        min_keyword_matches = eval_item.get("min_keyword_matches", 1)

        if reranker is None:
            retrieval_results = retriever.search(
                query=query,
                top_k=top_k,
            )
        else:
            candidate_results = retriever.search(
                query=query,
                top_k=first_stage_k,
            )

            retrieval_results = reranker.rerank(
                query=query,
                results=candidate_results,
                top_k=top_k,
            )

        first_hit_rank = find_first_hit_rank(
            retrieval_results=retrieval_results,
            expected_keywords=expected_keywords,
            min_keyword_matches=min_keyword_matches,
        )

        hit_1_scores.append(hit_at_rank(first_hit_rank, 1))
        hit_3_scores.append(hit_at_rank(first_hit_rank, min(3, top_k)))
        hit_k_scores.append(hit_at_rank(first_hit_rank, top_k))

        if first_hit_rank is None:
            mrr_scores.append(0.0)
            ranks.append(top_k + 1)
        else:
            mrr_scores.append(1.0 / first_hit_rank)
            ranks.append(first_hit_rank)

        if show_details:
            hit_status = "MISS" if first_hit_rank is None else f"HIT@{first_hit_rank}"
            print(
                f"[{method_name}] "
                f"Query {eval_index:02d}: {hit_status} | "
                f"query={query}"
            )

    return {
        "method": method_name,
        "hit@1": mean(hit_1_scores),
        "hit@3": mean(hit_3_scores),
        f"hit@{top_k}": mean(hit_k_scores),
        f"mrr@{top_k}": mean(mrr_scores),
        "avg_rank": mean(ranks),
    }


def print_summary_table(results: list[dict[str, Any]], top_k: int) -> None:
    hit_k_name = f"hit@{top_k}"
    mrr_k_name = f"mrr@{top_k}"

    print("\n========== RETRIEVAL EVALUATION ==========\n")

    print(
        f"{'Method':<32} "
        f"{'Hit@1':<10} "
        f"{'Hit@3':<10} "
        f"{f'Hit@{top_k}':<10} "
        f"{f'MRR@{top_k}':<10} "
        f"{'Avg Rank':<10}"
    )
    print("-" * 86)

    for result in results:
        print(
            f"{result['method']:<32} "
            f"{result['hit@1']:<10.3f} "
            f"{result['hit@3']:<10.3f} "
            f"{result[hit_k_name]:<10.3f} "
            f"{result[mrr_k_name]:<10.3f} "
            f"{result['avg_rank']:<10.3f}"
        )


def save_summary_csv(
    results: list[dict[str, Any]],
    output_csv: str,
) -> None:
    if not output_csv:
        return

    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = list(results[0].keys())

    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\nSaved evaluation summary to: {output_path}")


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

    print(f"PDF: {pdf_path}")
    print(f"Eval JSON: {eval_json_path}")
    print(f"Number of chunks: {len(chunks)}")
    print(f"Number of eval queries: {len(eval_queries)}")
    print(f"Top-K: {args.top_k}")
    print(f"Hybrid Alpha: {args.alpha}")
    print(f"Hybrid Candidate-K: {args.candidate_k}")
    print(f"Rerank Candidate-K: {args.rerank_candidate_k}")
    print(f"Retriever Weight: {args.retriever_weight}")
    print(
        "\nNote: This is keyword-based weak evaluation. "
        "It checks whether retrieved chunks contain expected keywords, "
        "not whether they are semantically sufficient."
    )

    tfidf_retriever = create_retriever(
        retriever_type="tfidf",
        chunks=chunks,
    )

    embedding_retriever = create_retriever(
        retriever_type="embedding",
        chunks=chunks,
        embedding_model=args.embedding_model,
    )

    hybrid_retriever = create_retriever(
        retriever_type="hybrid",
        chunks=chunks,
        embedding_model=args.embedding_model,
        alpha=args.alpha,
        candidate_k=args.candidate_k,
    )

    keyword_reranker = create_reranker(
        reranker_type="keyword",
    )

    score_fusion_reranker = create_reranker(
        reranker_type="score_fusion",
        retriever_weight=args.retriever_weight,
    )

    method_configs = [
        {
            "method_name": "tfidf",
            "retriever": tfidf_retriever,
            "reranker": None,
        },
        {
            "method_name": "embedding",
            "retriever": embedding_retriever,
            "reranker": None,
        },
        {
            "method_name": "hybrid",
            "retriever": hybrid_retriever,
            "reranker": None,
        },
        {
            "method_name": "tfidf+keyword_rerank",
            "retriever": tfidf_retriever,
            "reranker": keyword_reranker,
        },
        {
            "method_name": "hybrid+score_fusion_rerank",
            "retriever": hybrid_retriever,
            "reranker": score_fusion_reranker,
        },
    ]

    results = []

    for method_config in method_configs:
        result = evaluate_method(
            method_name=method_config["method_name"],
            retriever=method_config["retriever"],
            reranker=method_config["reranker"],
            eval_queries=eval_queries,
            top_k=args.top_k,
            rerank_candidate_k=args.rerank_candidate_k,
            show_details=args.show_details,
        )

        results.append(result)

    print_summary_table(
        results=results,
        top_k=args.top_k,
    )

    save_summary_csv(
        results=results,
        output_csv=args.output_csv,
    )


if __name__ == "__main__":
    main()