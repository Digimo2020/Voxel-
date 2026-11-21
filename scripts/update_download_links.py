"""Point README download buttons at the versioned files for CURRENT_VERSION.

Run after bumping src/utils/version.py:  python scripts/update_download_links.py
Every download then carries its version, e.g. Voxel-v1.1.23.exe.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
version = re.search(r'CURRENT_VERSION\s*=\s*"(v[\d.]+)"', (ROOT / "src/utils/version.py").read_text(encoding="utf-8")).group(1)
base = "https://github.com/Digimo2020/Voxel-/releases/download"

readme = ROOT / "README.md"
s = readme.read_text(encoding="utf-8")
s = re.sub(rf"{re.escape(base)}/v[\d.]+/Voxel-v[\d.]+\.exe", f"{base}/{version}/Voxel-{version}.exe", s)
s = re.sub(rf"{re.escape(base)}/v[\d.]+/Voxel-v[\d.]+\.dmg", f"{base}/{version}/Voxel-{version}.dmg", s)
s = re.sub(r"download `Voxel(-v[\d.]+)?\.exe`", f"download `Voxel-{version}.exe`", s)
readme.write_text(s, encoding="utf-8", newline="")
print(f"README download links now point to {version}")
