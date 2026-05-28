# 评估 TF-IDF、Embedding、Hybrid 以及 Rerank 后的检索效果
from pathlib import Path
import argparse
import csv
import json
import unicodedata
from datetime import datetime
from statistics import mean
from time import perf_counter
from typing import Any

from app.states import PaperState
from app.nodes.load_pdf import load_pdf_node
from app.nodes.split_text import split_text_node
from app.tools.retrievers.factory import create_retriever
from app.tools.rerankers.factory import create_reranker
from app.tools.query_expansion import HeuristicQueryExpander
from app.tools.retrievers.multi_query_retriever import MultiQueryRetriever


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
        "--output-csv",
        type=str,
        default="",
        help="Optional extra path to save evaluation summary as CSV.",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs/eval",
        help="Directory used for timestamped CSV and Markdown evaluation results.",
    )

    parser.add_argument(
        "--save-results",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Save timestamped CSV and Markdown results to --output-dir. Enabled by default.",
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


def percentile(values: list[float], percentile_value: float) -> float:
    if not values:
        return 0.0

    sorted_values = sorted(values)
    index = round((percentile_value / 100.0) * (len(sorted_values) - 1))
    index = max(0, min(index, len(sorted_values) - 1))

    return sorted_values[index]


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
    latencies_ms = []

    first_stage_k = max(top_k, rerank_candidate_k)

    for eval_index, eval_item in enumerate(eval_queries, start=1):
        query = eval_item["query"]
        expected_keywords = eval_item["expected_keywords"]
        min_keyword_matches = eval_item.get("min_keyword_matches", 1)

        start_time = perf_counter()

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

        latency_ms = (perf_counter() - start_time) * 1000.0
        latencies_ms.append(latency_ms)

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
                f"latency={latency_ms:.2f} ms | "
                f"query={query}"
            )

    return {
        "method": method_name,
        "num_queries": len(eval_queries),
        "hit_at_1": mean(hit_1_scores),
        "hit_at_3": mean(hit_3_scores),
        "hit_at_k": mean(hit_k_scores),
        "mrr_at_k": mean(mrr_scores),
        "avg_rank": mean(ranks),
        "avg_latency_ms": mean(latencies_ms),
        "min_latency_ms": min(latencies_ms),
        "max_latency_ms": max(latencies_ms),
        "p50_latency_ms": percentile(latencies_ms, 50),
        "p95_latency_ms": percentile(latencies_ms, 95),
    }

'''
def get_display_method_name(method_name: str) -> str:
    """
    将较长的方法名压缩成适合命令行展示的短名称。
    """

    aliases = {
        "tfidf": "tfidf",
        "embedding": "embedding",
        "hybrid": "hybrid",
        "tfidf+keyword_rerank": "tfidf+kw-rerank",
        "hybrid+score_fusion_rerank": "hybrid+fusion",
        "hybrid+query_expansion": "hybrid+qe",
        "hybrid+query_expansion+score_fusion_rerank": "hybrid+qe+fusion",
    }

    return aliases.get(method_name, method_name)


def print_summary_table(results: list[dict[str, Any]], top_k: int) -> None:
    hit_k_key = f"hit@{top_k}"
    mrr_k_key = f"mrr@{top_k}"

    method_names = [
        get_display_method_name(result["method"])
        for result in results
    ]

    method_width = max(
        len("Method"),
        max(len(name) for name in method_names),
    )

    num_width = 9

    print("\n========== RETRIEVAL EVALUATION ==========\n")

    header = (
        f"{'Method':<{method_width}}  "
        f"{'Hit@1':>{num_width}}  "
        f"{'Hit@3':>{num_width}}  "
        f"{f'Hit@{top_k}':>{num_width}}  "
        f"{f'MRR@{top_k}':>{num_width}}  "
        f"{'AvgRank':>{num_width}}"
    )

    print(header)
    print("-" * len(header))

    for result in results:
        method_name = get_display_method_name(result["method"])

        print(
            f"{method_name:<{method_width}}  "
            f"{result['hit@1']:>{num_width}.3f}  "
            f"{result['hit@3']:>{num_width}.3f}  "
            f"{result[hit_k_key]:>{num_width}.3f}  "
            f"{result[mrr_k_key]:>{num_width}.3f}  "
            f"{result['avg_rank']:>{num_width}.3f}"
        )

    print("\nLegend:")
    print("- kw-rerank: keyword reranker")
    print("- fusion: score fusion reranker")
    print("- qe: query expansion / multi-query retrieval")
'''


def print_summary_table(results: list[dict[str, Any]], top_k: int) -> None:
    method_width = max(
        len("Method"),
        max(len(result["method"]) for result in results),
    )

    print("\n========== RETRIEVAL EVALUATION ==========\n")

    print(
        f"{'Method':<{method_width}} "
        f"{'Hit@1':<10} "
        f"{'Hit@3':<10} "
        f"{f'Hit@{top_k}':<10} "
        f"{f'MRR@{top_k}':<10} "
        f"{'Avg Rank':<10} "
        f"{'Avg Lat(ms)':<12}"
    )
    print("-" * (method_width + 69))

    for result in results:
        print(
            f"{result['method']:<{method_width}} "
            f"{result['hit_at_1']:<10.3f} "
            f"{result['hit_at_3']:<10.3f} "
            f"{result['hit_at_k']:<10.3f} "
            f"{result['mrr_at_k']:<10.3f} "
            f"{result['avg_rank']:<10.3f} "
            f"{result['avg_latency_ms']:<12.2f}"
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

    print(f"\nSaved evaluation summary CSV to: {output_path}")


def save_summary_markdown(
    results: list[dict[str, Any]],
    output_markdown: str,
    run_time: str,
    eval_json_path: Path,
    top_k: int,
) -> None:
    if not output_markdown:
        return

    output_path = Path(output_markdown)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    method_names = [result["method"] for result in results]

    lines = [
        "# Retriever Evaluation Results",
        "",
        f"- Run Time: {run_time}",
        f"- Eval Queries: `{eval_json_path}`",
        f"- Top-K: {top_k}",
        f"- Methods: {', '.join(method_names)}",
        "",
        "## Method Summary",
        "",
        "| Method | Num Queries | Hit@1 | Hit@3 | Hit@K | MRR@K | Avg Rank | Avg Latency (ms) | Min Latency (ms) | Max Latency (ms) | P50 Latency (ms) | P95 Latency (ms) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for result in results:
        lines.append(
            "| "
            f"{result['method']} | "
            f"{result['num_queries']} | "
            f"{result['hit_at_1']:.3f} | "
            f"{result['hit_at_3']:.3f} | "
            f"{result['hit_at_k']:.3f} | "
            f"{result['mrr_at_k']:.3f} | "
            f"{result['avg_rank']:.3f} | "
            f"{result['avg_latency_ms']:.2f} | "
            f"{result['min_latency_ms']:.2f} | "
            f"{result['max_latency_ms']:.2f} | "
            f"{result['p50_latency_ms']:.2f} | "
            f"{result['p95_latency_ms']:.2f} |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Latency does not include retriever initialization, embedding model loading, or FAISS index loading/building time.",
            "- Latency includes each method's per-query retrieval cost, including query expansion, multi-query retrieval, and reranking when enabled.",
            "- Current relevance judgment is keyword-based weak evaluation. It checks expected keyword matches in retrieved chunks, not full semantic sufficiency.",
        ]
    )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved evaluation summary Markdown to: {output_path}")


def build_timestamped_output_paths(
    output_dir: str,
    timestamp: str,
) -> tuple[str, str]:
    output_path = Path(output_dir)
    csv_path = output_path / f"retriever_eval_{timestamp}.csv"
    markdown_path = output_path / f"retriever_eval_{timestamp}.md"

    return str(csv_path), str(markdown_path)


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
    print(f"Query Expansion Max Queries: {args.query_expansion_max_queries}")
    print(f"Multi-query Per-query K: {args.multi_query_per_query_k}")
    print(f"Multi-query RRF K: {args.multi_query_rrf_k}")
    print(f"Save Results: {args.save_results}")
    print(f"Output Dir: {args.output_dir}")
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

    query_expander = HeuristicQueryExpander()

    hybrid_query_expansion_retriever = MultiQueryRetriever(
        base_retriever=hybrid_retriever,
        query_expander=query_expander,
        max_queries=args.query_expansion_max_queries,
        per_query_k=args.multi_query_per_query_k,
        rrf_k=args.multi_query_rrf_k,
    )

    keyword_reranker = create_reranker(
        reranker_type="keyword",
    )

    score_fusion_reranker = create_reranker(
        reranker_type="score_fusion",
        retriever_weight=args.retriever_weight,
    )

    section_prior_reranker = create_reranker(
        reranker_type="section_prior",
        retriever_weight=args.retriever_weight,
    )

    robotics_tag_prior_reranker = create_reranker(
        reranker_type="robotics_tag_prior",
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
            "method_name": "tfidf+section_prior_rerank",
            "retriever": tfidf_retriever,
            "reranker": section_prior_reranker,
        },
        {
            "method_name": "tfidf+robotics_tag_prior_rerank",
            "retriever": tfidf_retriever,
            "reranker": robotics_tag_prior_reranker,
        },
        {
            "method_name": "hybrid+score_fusion_rerank",
            "retriever": hybrid_retriever,
            "reranker": score_fusion_reranker,
        },
        {
            "method_name": "hybrid+section_prior_rerank",
            "retriever": hybrid_retriever,
            "reranker": section_prior_reranker,
        },
        {
            "method_name": "hybrid+robotics_tag_prior_rerank",
            "retriever": hybrid_retriever,
            "reranker": robotics_tag_prior_reranker,
        },
        {
            "method_name": "hybrid+query_expansion",
            "retriever": hybrid_query_expansion_retriever,
            "reranker": None,
        },
        {
            "method_name": "hybrid+query_expansion+score_fusion_rerank",
            "retriever": hybrid_query_expansion_retriever,
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

    if args.save_results:
        run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_csv, output_markdown = build_timestamped_output_paths(
            output_dir=args.output_dir,
            timestamp=run_timestamp,
        )

        save_summary_csv(
            results=results,
            output_csv=output_csv,
        )

        save_summary_markdown(
            results=results,
            output_markdown=output_markdown,
            run_time=run_timestamp,
            eval_json_path=eval_json_path,
            top_k=args.top_k,
        )


if __name__ == "__main__":
    main()
