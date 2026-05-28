from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.tools.retrievers.schemas import RetrievalResult  # noqa: E402
from app.tools.text_splitter import split_text_into_chunks  # noqa: E402
from app.tools.trace_writer import build_trace_from_state  # noqa: E402


def assert_chunk_robotics_metadata() -> None:
    text = """
    Abstract
    This LiDAR-inertial SLAM system is evaluated on KITTI. The odometry
    front-end reports ATE and RPE while preserving real-time latency.
    """

    chunks = split_text_into_chunks(
        text=text,
        chunk_size=500,
        chunk_overlap=50,
    )

    assert len(chunks) == 1

    chunk = chunks[0]
    assert chunk.chunk_id == 0
    assert chunk.start_char == 0
    assert chunk.end_char <= len(text.strip())
    assert chunk.section_title == "Abstract"

    assert chunk.robotics_tags["sensor_modality"] == ["LiDAR", "IMU"]
    assert chunk.robotics_tags["dataset"] == ["KITTI"]
    assert chunk.robotics_tags["metric"] == ["ATE", "RPE", "latency"]
    assert chunk.robotics_tags["task_type"] == ["SLAM", "odometry"]
    assert chunk.robotics_tags["system_module"] == ["front-end"]
    assert chunk.robotics_tags["deployment_constraint"] == ["real-time", "latency"]
    assert chunk.robotics_tag_count == len(chunk.robotics_flat_tags)
    assert "sensor_modality:LiDAR" in chunk.robotics_flat_tags


def assert_empty_robotics_metadata() -> None:
    chunks = split_text_into_chunks(
        text="Abstract\nThis paper studies optimization theory.",
        chunk_size=500,
        chunk_overlap=50,
    )

    assert len(chunks) == 1
    assert chunks[0].robotics_tags == {}
    assert chunks[0].robotics_tag_count == 0
    assert chunks[0].robotics_flat_tags == []


def assert_trace_robotics_summary() -> None:
    chunks = split_text_into_chunks(
        text="Abstract\nLiDAR SLAM on KITTI reports ATE with real-time runtime.",
        chunk_size=500,
        chunk_overlap=50,
    )
    retrieval_results = [
        RetrievalResult(
            chunk=chunks[0],
            score=0.9,
            source="test",
            metadata={"rank": 1},
        )
    ]

    trace = build_trace_from_state(
        {
            "pdf_path": "data/example.pdf",
            "query": "LiDAR SLAM KITTI ATE",
            "top_k": 1,
            "chunks": chunks,
            "retrieval_results": retrieval_results,
            "retrieved_context": "preview only",
            "retrieval_evidence": "evidence only",
        }
    )

    chunk_summary = trace["paper"]["chunks"]
    assert chunk_summary["robotics_tag_summary"]["total_tagged_chunks"] == 1
    assert chunk_summary["robotics_tag_summary"]["tag_counts_by_category"]["sensor_modality"] == 1

    retrieved_preview = trace["retrieval"]["retrieval_results"]["preview_items"][0]
    assert retrieved_preview["robotics_tags"]["sensor_modality"] == ["LiDAR"]
    assert "dataset:KITTI" in retrieved_preview["robotics_flat_tags"]


def main() -> None:
    assert_chunk_robotics_metadata()
    print("chunk robotics metadata passed")

    assert_empty_robotics_metadata()
    print("empty robotics metadata passed")

    assert_trace_robotics_summary()
    print("trace robotics summary passed")

    print("All chunk robotics metadata smoke tests passed.")


if __name__ == "__main__":
    main()
