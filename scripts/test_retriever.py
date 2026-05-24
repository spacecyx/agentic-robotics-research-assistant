# 检索测试脚本
import argparse

from app.tools.pdf_loader_pro import load_pdf_text, clean_paper_text
from app.tools.text_splitter import split_text_into_chunks
from app.tools.retrievers.factory import create_retriever


def print_retrieval_results(results, max_chars: int = 700) -> None:
    if not results:
        print("No retrieval results.")
        return

    for rank, result in enumerate(results, start=1):
        chunk = result.chunk

        print("=" * 100)
        print(f"Rank: {rank}")
        print(f"Chunk ID: {chunk.chunk_id}")
        print(f"Score: {result.score:.4f}")
        print(f"Source: {result.source}")
        print(f"Char Range: {chunk.start_char} - {chunk.end_char}")
        print("-" * 100)
        print(chunk.text[:max_chars])
        print()


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--pdf",
        type=str,
        required=True,
        help="Path to the PDF file.",
    )

    parser.add_argument(
        "--query",
        type=str,
        required=True,
        help="Query for retrieval.",
    )

    parser.add_argument(
        "--top-k",
        type=int,
        # 取前3
        default=3, 
        help="Number of retrieved chunks.",
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        # 单块文本大小
        default=800,
        help="Chunk size in characters.",
    )

    parser.add_argument(
        "--chunk-overlap",
        type=int,
        # 文本分块时 保留120的上下文重叠
        default=120,
        help="Chunk overlap in characters.",
    )

    args = parser.parse_args()

    print(f"Loading PDF: {args.pdf}")
    raw_text = load_pdf_text(args.pdf)
    clean_text = clean_paper_text(raw_text)

    chunks = split_text_into_chunks(
        text=clean_text,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )

    print(f"Original text length: {len(raw_text)}")
    print(f"Cleaned text length: {len(clean_text)}")
    print(f"Total chunks: {len(chunks)}")
    print(f"Query: {args.query}")
    print(f"Top K: {args.top_k}")

    retriever = create_retriever(
        retriever_type="tfidf",
        chunks=chunks,
    )

    results = retriever.search(
        query=args.query,
        top_k=args.top_k,
    )

    print_retrieval_results(results)


if __name__ == "__main__":
    main()


# 项目根目录下运行测试代码：python -m scripts.test_retriever --pdf ./data/resnet.pdf --query "shortcut connection" 
