from __future__ import annotations


def chunk_markdown(content: str) -> list[tuple[str, str]]:
    chunks: list[tuple[str, str]] = []
    current_heading = "document"
    current_lines: list[str] = []
    for line in content.splitlines():
        if line.startswith("#") and current_lines:
            chunks.append((current_heading, "\n".join(current_lines).strip()))
            current_lines = []
        if line.startswith("#"):
            current_heading = line.lstrip("# ").strip() or "section"
        current_lines.append(line)
    if current_lines:
        chunks.append((current_heading, "\n".join(current_lines).strip()))
    return chunks or [("document", content.strip())]
