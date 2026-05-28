from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.tools.retrieval_quality import evaluate_retrieval_quality  # noqa: E402
from app.tools.retrievers.schemas import RetrievalResult  # noqa: E402
from app.tools.text_splitter import TextChunk, build_robotics_chunk_metadata  # noqa: E402


def make_chunk(
    text: str,
    score: float,
    section_title: str | None = None,
) -> RetrievalResult:
    robotics_tags, robotics_tag_count, robotics_flat_tags = build_robotics_chunk_metadata(text)
    chunk = TextChunk(
        chunk_id=0,
        text=text,
        start_char=0,
        end_char=len(text),
        section_title=section_title,
        robotics_tags=robotics_tags,
        robotics_tag_count=robotics_tag_count,
        robotics_flat_tags=robotics_flat_tags,
    )

    return RetrievalResult(
        chunk=chunk,
        score=score,
        source="test",
        metadata={"rank": 1},
    )


def assert_empty_retrieval_quality() -> None:
    quality = evaluate_retrieval_quality(
        query="What are the main results?",
        retrieved_chunks=[],
        top_k=3,
    )

    assert quality["quality_label"] == "empty"
    assert quality["recommended_action"] == "fallback"
    assert "no_retrieved_chunks" in quality["reasons"]


def assert_high_score_chunk_quality() -> None:
    result = make_chunk(
        text="The method section describes the core algorithm.",
        score=0.8,
        section_title="Method",
    )
    quality = evaluate_retrieval_quality(
        query="What is the main method?",
        retrieved_chunks=[result],
        top_k=1,
        query_intent="method",
    )

    assert quality["quality_label"] == "good"
    assert quality["recommended_action"] == "proceed"
    assert quality["top_score"] == 0.8


def assert_low_score_chunk_quality() -> None:
    result = make_chunk(
        text="A weak unrelated chunk.",
        score=0.001,
        section_title="Introduction",
    )
    quality = evaluate_retrieval_quality(
        query="What is the main method?",
        retrieved_chunks=[result],
        top_k=1,
        query_intent="method",
    )

    assert quality["quality_label"] == "weak"
    assert quality["recommended_action"] == "expand_query"
    assert "low_top_score" in quality["reasons"]
    assert "low_avg_score" in quality["reasons"]


def assert_dataset_metric_query_without_tags_is_weak() -> None:
    result = make_chunk(
        text="The paper discusses training details but no benchmark metrics.",
        score=0.7,
        section_title="Method",
    )
    quality = evaluate_retrieval_quality(
        query="What dataset and metrics are used?",
        retrieved_chunks=[result],
        top_k=1,
        query_intent="metric",
    )

    assert quality["quality_label"] == "weak"
    assert quality["recommended_action"] == "expand_query"
    assert "missing_experiment_or_result_section" in quality["reasons"]
    assert "missing_dataset_or_metric_tags" in quality["reasons"]


def assert_sensor_query_with_lidar_imu_tags_is_good() -> None:
    result = make_chunk(
        text="The LiDAR-inertial SLAM system uses LiDAR and IMU measurements.",
        score=0.7,
        section_title="Method",
    )
    quality = evaluate_retrieval_quality(
        query="What sensors are used?",
        retrieved_chunks=[result],
        top_k=1,
        query_intent="sensor",
    )

    assert quality["quality_label"] == "good"
    assert quality["recommended_action"] == "proceed"
    assert quality["robotics_tag_coverage"]["category_counts"]["sensor_modality"] == 2


def main() -> None:
    assert_empty_retrieval_quality()
    print("empty retrieval quality passed")

    assert_high_score_chunk_quality()
    print("high score chunk quality passed")

    assert_low_score_chunk_quality()
    print("low score chunk quality passed")

    assert_dataset_metric_query_without_tags_is_weak()
    print("dataset/metric missing evidence quality passed")

    assert_sensor_query_with_lidar_imu_tags_is_good()
    print("sensor tag coverage quality passed")

    print("All retrieval_quality smoke tests passed.")


if __name__ == "__main__":
    main()
