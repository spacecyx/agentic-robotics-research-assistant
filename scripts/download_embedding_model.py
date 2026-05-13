# 需要保证网络连通
from sentence_transformers import SentenceTransformer


def main() -> None:
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    output_path = "models/all-MiniLM-L6-v2"

    model = SentenceTransformer(model_name)
    model.save(output_path)

    print(f"saved to {output_path}")


if __name__ == "__main__":
    main()