from pathlib import Path

from app.tools.pdf_loader_pro import (
    clean_paper_text,
    extract_paper_title,
    load_pdf_text,
)


def test_pdf(pdf_path: str):
    raw_text = load_pdf_text(pdf_path)
    paper_text = clean_paper_text(raw_text)

    fallback_title = Path(pdf_path).stem
    paper_title = extract_paper_title(
        raw_text=raw_text,
        fallback_title=fallback_title,
    )

    print("\n========== PDF LOAD SUCCESS ==========")
    print(f"PDF path: {pdf_path}")
    print(f"Paper title: {paper_title}")
    print(f"Raw text length: {len(raw_text)}")
    print(f"Cleaned text length: {len(paper_text)}")
    print("========== PREVIEW ==========")
    print(paper_text[:500])


def main():
    test_pdf("./data/resnet.pdf")
    test_pdf("./data/transformer.pdf")


if __name__ == "__main__":
    main()


# 项目根目录下运行测试代码：python -m scripts.test_pdf_loader
