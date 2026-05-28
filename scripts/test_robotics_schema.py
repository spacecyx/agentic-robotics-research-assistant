from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.tools.robotics_schema import (  # noqa: E402
    extract_robotics_tags,
    flatten_robotics_tags,
    has_robotics_tags,
)


def assert_representative_robotics_chunk() -> None:
    text = """
    We evaluate a LiDAR-inertial SLAM front-end on KITTI and EuRoC.
    The odometry module reports ATE, RPE, and RMSE while maintaining
    real-time runtime under dynamic scenes.
    """

    tags = extract_robotics_tags(text)

    assert tags["sensor_modality"] == ["LiDAR", "IMU"]
    assert tags["dataset"] == ["KITTI", "EuRoC"]
    assert tags["metric"] == ["ATE", "RPE", "RMSE", "runtime"]
    assert tags["task_type"] == ["SLAM", "odometry"]
    assert tags["system_module"] == ["front-end"]
    assert tags["deployment_constraint"] == ["real-time", "dynamic scenes"]
    assert has_robotics_tags(tags) is True

    flattened = flatten_robotics_tags(tags)
    assert "sensor_modality:LiDAR" in flattened
    assert "dataset:KITTI" in flattened
    assert "deployment_constraint:real-time" in flattened


def assert_case_and_phrase_robustness() -> None:
    text = """
    The RGBD camera pipeline performs point cloud registration on ScanNet.
    It uses ICP, IoU, mean average precision, and F score under occlusions.
    """

    tags = extract_robotics_tags(text)

    assert tags["sensor_modality"] == ["camera", "RGB-D"]
    assert tags["dataset"] == ["ScanNet"]
    assert tags["metric"] == ["mAP", "IoU", "F-score"]
    assert tags["task_type"] == ["registration"]
    assert tags["system_module"] == ["scan matching"]
    assert tags["deployment_constraint"] == ["occlusion"]


def assert_empty_and_non_robotics_text() -> None:
    empty_tags = extract_robotics_tags("")
    assert has_robotics_tags(empty_tags) is False
    assert flatten_robotics_tags(empty_tags) == []

    generic_tags = extract_robotics_tags("This paper studies maps in graph theory.")
    assert has_robotics_tags(generic_tags) is False


def main() -> None:
    assert_representative_robotics_chunk()
    print("representative robotics chunk passed")

    assert_case_and_phrase_robustness()
    print("case and phrase robustness passed")

    assert_empty_and_non_robotics_text()
    print("empty and non-robotics text passed")

    print("All robotics_schema smoke tests passed.")


if __name__ == "__main__":
    main()
