from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.tools.rerankers.factory import create_reranker  # noqa: E402
from app.tools.retrievers.schemas import RetrievalResult  # noqa: E402
from app.tools.text_splitter import TextChunk, build_robotics_chunk_metadata  # noqa: E402


def make_chunk(chunk_id: int, text: str) -> TextChunk:
    robotics_tags, robotics_tag_count, robotics_flat_tags = build_robotics_chunk_metadata(text)

    return TextChunk(
        chunk_id=chunk_id,
        text=text,
        start_char=0,
        end_char=len(text),
        robotics_tags=robotics_tags,
        robotics_tag_count=robotics_tag_count,
        robotics_flat_tags=robotics_flat_tags,
    )


def assert_robotics_tags_raise_relevant_chunk() -> None:
    generic_chunk = make_chunk(
        0,
        "This chunk discusses generic neural network optimization and training.",
    )
    robotics_chunk = make_chunk(
        1,
        "LiDAR SLAM odometry on KITTI reports ATE and real-time latency.",
    )

    results = [
        RetrievalResult(
            chunk=generic_chunk,
            score=0.70,
            source="test",
            metadata={"rank": 1},
        ),
        RetrievalResult(
            chunk=robotics_chunk,
            score=0.50,
            source="test",
            metadata={"rank": 2},
        ),
    ]

    reranker = create_reranker(
        reranker_type="robotics_tag_prior",
        retriever_weight=0.5,
    )
    reranked = reranker.rerank(
        query="Which LiDAR SLAM method reports KITTI ATE and real-time latency?",
        results=results,
        top_k=2,
    )

    assert reranked[0].chunk.chunk_id == 1
    assert reranked[0].metadata["query_intent"] == "sensor"
    assert reranked[0].metadata["robotics_tag_score"] > 0.0
    assert "sensor_modality:LiDAR" in reranked[0].metadata["matched_robotics_tags"]
    assert "dataset:KITTI" in reranked[0].metadata["matched_robotics_tags"]
    assert reranked[0].metadata["original_score"] == 0.50
    assert reranked[0].metadata["final_score"] == reranked[0].score


def main() -> None:
    assert_robotics_tags_raise_relevant_chunk()
    print("robotics tag prior reranker ranking lift passed")
    print("All robotics_tag_prior reranker smoke tests passed.")


if __name__ == "__main__":
    main()
