"""Voxel application version and repository metadata."""
import re

CURRENT_VERSION = "v1.0.01"
GITHUB_REPO_URL = "https://github.com/Digimo2020/Voxel---V.002"


def parse_version(ver_str: str) -> tuple[int, int, int]:
    """Parse a version such as v1.0.01 into integer components."""
    match = re.match(r"^v?(\d+)\.(\d+)\.(\d+)$", ver_str.strip())
    if match:
        return int(match.group(1)), int(match.group(2)), int(match.group(3))
    return 1, 0, 1


def format_version(major: int, minor: int, patch: int) -> str:
    return f"v{major}.{minor}.{patch:02d}"


def bump_version(ver_str: str) -> str:
    major, minor, patch = parse_version(ver_str)
    patch += 1
    if patch >= 10:
        patch = 0
        minor += 1
        if minor >= 10:
            minor = 0
            major += 1
    return format_version(major, minor, patch)
