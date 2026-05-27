# 文本切分测试脚本

import argparse

from app.tools.pdf_loader_pro import load_pdf_text, clean_paper_text
from app.tools.text_splitter import (
    build_page_spans_from_raw_text,
    split_text_into_chunks,
    preview_chunks,
)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--pdf",
        type=str,
        default="./data/transformer.pdf",
        help="Path to the PDF file.",
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=800,
        help="Chunk size in characters.",
    )

    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=120,
        help="Chunk overlap in characters.",
    )

    args = parser.parse_args()

    print(f"Loading PDF: {args.pdf}")

    # pdf 文本内容获取
    raw_text = load_pdf_text(args.pdf)
    # 去除空格，制表符，空行的文本清洗处理
    clean_text = clean_paper_text(raw_text)
    page_spans = build_page_spans_from_raw_text(
        raw_text=raw_text,
        cleaned_text=clean_text,
    )

    chunks = split_text_into_chunks(
        # text=raw_text,
        text=clean_text,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        page_spans=page_spans,
    )

    print(f"Original text length: {len(raw_text)}")
    print(f"Chunk size: {args.chunk_size}")
    print(f"Chunk overlap: {args.chunk_overlap}")

    # 这里只做前 3 个 chunck(分块) 的展示
    preview_chunks(chunks)


if __name__ == "__main__":
    main()

# 项目根目录下运行测试代码：python -m scripts.test_text_splitter --pdf ./data/resnet.pdf
