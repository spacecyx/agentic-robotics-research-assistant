# 检索测试脚本
import argparse

from app.tools.pdf_loader_pro import load_pdf_text, clean_paper_text
from app.tools.text_splitter import split_text_into_chunks
from app.tools.simple_retriever import retrieve_top_k, print_retrieval_results


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

    results = retrieve_top_k(
        query=args.query,
        chunks=chunks,
        top_k=args.top_k,
    )

    print_retrieval_results(results)


if __name__ == "__main__":
    main()


# 项目根目录下运行测试代码：python -m scripts.test_retriever --pdf ./data/resnet.pdf --query "shortcut connection" 