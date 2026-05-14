# 构建并保存 FAISS 本地向量索引 | 知识库的预处理与持久化
# 运行方式：
# python -m scripts.build_faiss_index --pdf data/resnet.pdf

from pathlib import Path
import argparse

from app.states import PaperState
from app.nodes.load_pdf import load_pdf_node
from app.nodes.split_text import split_text_node
from app.tools.vector_store.faiss_store import FaissVectorStore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build local FAISS index for a paper PDF."
    )

    parser.add_argument(
        "--pdf",
        type=str,
        required=True,
        help="Path to the input paper PDF.",
    )

    parser.add_argument(
        "--index-dir",
        type=str,
        default="",
        help="Directory to save FAISS index files. Default: data/index/<pdf_stem>",
    )

    parser.add_argument(
        "--embedding-model",
        type=str,
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Embedding model name or local model path.",
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


def main() -> None:
    args = parse_args()

    pdf_path = Path(args.pdf)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {args.pdf}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Input file must be a PDF: {args.pdf}")

    index_dir = (
        Path(args.index_dir)
        if args.index_dir
        else Path("data/index") / pdf_path.stem
    )

    chunks = prepare_chunks(str(pdf_path))

    vector_store = FaissVectorStore.build(
        chunks=chunks,
        model_name=args.embedding_model,
    )

    vector_store.save(index_dir)

    print("\n========== FAISS INDEX BUILT ==========\n")
    print(f"PDF: {pdf_path}")
    print(f"Index dir: {index_dir}")
    print(f"Number of chunks: {len(chunks)}")
    print(f"Embedding dim: {vector_store.metadata['embedding_dim']}")
    print(f"Model: {args.embedding_model}")
    print("\nSaved files:")
    print(f"- {index_dir / FaissVectorStore.INDEX_FILE}")
    print(f"- {index_dir / FaissVectorStore.CHUNKS_FILE}")
    print(f"- {index_dir / FaissVectorStore.EMBEDDINGS_FILE}")
    print(f"- {index_dir / FaissVectorStore.META_FILE}")


if __name__ == "__main__":
    main()