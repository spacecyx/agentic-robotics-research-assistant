"""
Rule-based robotics metadata extraction for paper chunks.

The functions in this module are intentionally lightweight and offline-only.
They provide normalized robotics-aware tags that can later be attached to
chunk metadata or consumed by a tag-prior reranker.
"""

from __future__ import annotations

import re


ROBOTICS_TAG_PATTERNS: dict[str, dict[str, tuple[str, ...]]] = {
    "sensor_modality": {
        "LiDAR": (r"\blidar\b", r"\blaser\s+scanner(s)?\b"),
        "camera": (r"\bcamera(s)?\b", r"\bmonocular\b", r"\brgb\s+image(s)?\b"),
        "stereo": (r"\bstereo\b", r"\bstereo\s+camera(s)?\b"),
        "RGB-D": (r"\brgb[-\s]?d\b", r"\bdepth\s+camera(s)?\b"),
        "IMU": (r"\bimu\b", r"\binertial\b", r"\binertial\s+measurement\s+unit(s)?\b"),
        "radar": (r"\bradar\b", r"\bmillimeter[-\s]?wave\b", r"\bmmwave\b"),
        "GNSS": (r"\bgnss\b", r"\bgps\b", r"\bglobal\s+navigation\s+satellite\s+system\b"),
    },
    "dataset": {
        "KITTI": (r"\bkitti\b",),
        "SemanticKITTI": (r"\bsemantic[-\s]?kitti\b",),
        "nuScenes": (r"\bnuscenes\b",),
        "Waymo": (r"\bwaymo\b",),
        "TUM": (r"\btum\b", r"\btum\s+rgb[-\s]?d\b"),
        "EuRoC": (r"\beuroc\b", r"\beuroc\s+mav\b"),
        "ScanNet": (r"\bscannet\b",),
        "ModelNet": (r"\bmodelnet\b", r"\bmodelnet40\b"),
        "S3DIS": (r"\bs3dis\b",),
    },
    "metric": {
        "ATE": (r"\bate\b", r"\babsolute\s+trajectory\s+error\b"),
        "RPE": (r"\brpe\b", r"\brelative\s+pose\s+error\b"),
        "RMSE": (r"\brmse\b", r"\broot\s+mean\s+square\s+error\b"),
        "mAP": (r"(?-i:\bmAP\b)", r"\bmean\s+average\s+precision\b"),
        "IoU": (r"\biou\b", r"\bintersection\s+over\s+union\b"),
        "Chamfer": (r"\bchamfer\b", r"\bchamfer\s+distance\b"),
        "F-score": (r"\bf[-\s]?score\b",),
        "FPS": (r"\bfps\b", r"\bframes\s+per\s+second\b"),
        "runtime": (r"\brun[-\s]?time\b", r"\bruntime\b"),
        "latency": (r"\blatency\b", r"\binference\s+time\b"),
    },
    "task_type": {
        "SLAM": (r"\bslam\b", r"\bsimultaneous\s+localization\s+and\s+mapping\b"),
        "localization": (r"\blocali[sz]ation\b", r"\bpose\s+estimation\b"),
        "mapping": (r"\bmapping\b", r"\bmap\s+building\b"),
        "odometry": (r"\bodometry\b", r"\bvisual\s+odometry\b", r"\blidar\s+odometry\b"),
        "detection": (r"\bdetection\b", r"\bobject\s+detection\b"),
        "segmentation": (r"\bsegmentation\b", r"\bsemantic\s+segmentation\b"),
        "registration": (r"\bregistration\b", r"\bpoint\s+cloud\s+registration\b"),
        "tracking": (r"\btracking\b", r"\bobject\s+tracking\b"),
        "reconstruction": (r"\breconstruction\b", r"\b3d\s+reconstruction\b"),
    },
    "system_module": {
        "front-end": (r"\bfront[-\s]?end\b", r"\bfrontend\b"),
        "back-end": (r"\bback[-\s]?end\b", r"\bbackend\b"),
        "loop closure": (r"\bloop\s+closure\b", r"\bplace\s+recognition\b"),
        "pose graph": (r"\bpose\s+graph\b", r"\bgraph\s+optimization\b"),
        "bundle adjustment": (r"\bbundle\s+adjustment\b", r"\bba\b"),
        "scan matching": (r"\bscan\s+matching\b", r"\bicp\b"),
        "map optimization": (r"\bmap\s+optimization\b", r"\bmapping\s+optimization\b"),
    },
    "deployment_constraint": {
        "real-time": (r"\breal[-\s]?time\b", r"\bonline\b"),
        "memory": (r"\bmemory\b", r"\bmemory\s+footprint\b"),
        "compute": (r"\bcompute\b", r"\bcomputation(al)?\s+cost\b"),
        "latency": (r"\blatency\b", r"\blow[-\s]?latency\b"),
        "robustness": (r"\brobust(ness)?\b",),
        "dynamic scenes": (r"\bdynamic\s+scene(s)?\b", r"\bdynamic\s+environment(s)?\b"),
        "occlusion": (r"\bocclusion(s)?\b", r"\boccluded\b"),
        "calibration": (r"\bcalibration\b", r"\bcalibrated\b"),
    },
}


def extract_robotics_tags(text: str) -> dict[str, list[str]]:
    """
    Extract normalized robotics-aware tags from chunk text.

    Args:
        text: A paper chunk or other short text span.

    Returns:
        A dict with stable category keys and normalized tag names.
    """

    tags: dict[str, list[str]] = {
        category: []
        for category in ROBOTICS_TAG_PATTERNS
    }

    if not text or not text.strip():
        return tags

    for category, tag_patterns in ROBOTICS_TAG_PATTERNS.items():
        for tag_name, patterns in tag_patterns.items():
            if any(_matches_pattern(text, pattern) for pattern in patterns):
                tags[category].append(tag_name)

    return tags


def has_robotics_tags(tags: dict) -> bool:
    """
    Return True if at least one robotics tag is present.
    """

    return any(bool(values) for values in tags.values())


def flatten_robotics_tags(tags: dict) -> list[str]:
    """
    Flatten category-tag pairs into stable strings for scoring or logging.

    Example:
        {"sensor_modality": ["LiDAR"]} -> ["sensor_modality:LiDAR"]
    """

    flattened_tags: list[str] = []

    for category in ROBOTICS_TAG_PATTERNS:
        values = tags.get(category, [])

        if not isinstance(values, list):
            continue

        for value in values:
            flattened_tags.append(f"{category}:{value}")

    return flattened_tags


def _matches_pattern(text: str, pattern: str) -> bool:
    return re.search(pattern, text, flags=re.IGNORECASE) is not None
