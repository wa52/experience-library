from __future__ import annotations

from pathlib import Path


def scan_markdown_files(base_path: Path) -> list[Path]:
    return sorted(base_path.rglob("*.md"))
