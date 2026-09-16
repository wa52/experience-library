from __future__ import annotations


def split_front_matter(raw_text: str) -> tuple[str, str]:
    if not raw_text.startswith("---"):
        return "", raw_text
    parts = raw_text.split("---", 2)
    if len(parts) < 3:
        return "", raw_text
    return parts[1], parts[2]
