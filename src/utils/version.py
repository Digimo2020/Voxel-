"""
Version definitions and rollover logic according to user specification:
Format: v<Major>.<Minor>.<Patch:02d>  (e.g., v1.0.01)
- Every 10th patch cycle, patch rolls to 00 and minor increments by 1.
- Every 10th minor cycle, minor rolls to 0 and major increments by 1.
"""
import re

CURRENT_VERSION = "v1.0.01"
GITHUB_REPO_URL = "https://github.com/Digimo2020/Voxel-"


def parse_version(ver_str: str) -> tuple:
    """Parses 'v1.0.01' into (major: int, minor: int, patch: int)."""
    m = re.match(r"^v?(\d+)\.(\d+)\.(\d+)$", ver_str.strip())
    if m:
        return int(m.group(1)), int(m.group(2)), int(m.group(3))
    return 1, 0, 1


def format_version(major: int, minor: int, patch: int) -> str:
    """Formats components back into v<Major>.<Minor>.<Patch:02d>."""
    return f"v{major}.{minor}.{patch:02d}"


def bump_version(ver_str: str) -> str:
    """
    Bumps version according to the specified 10-cycle rollover rule:
    e.g. v1.0.01 -> v1.0.02 -> ... -> v1.0.09 -> v1.1.00
    e.g. v1.9.09 -> v2.0.00
    """
    major, minor, patch = parse_version(ver_str)
    patch += 1
    if patch >= 10:
        patch = 0
        minor += 1
        if minor >= 10:
            minor = 0
            major += 1
    return format_version(major, minor, patch)
