from __future__ import annotations

from typing import Any

from knowledge_agent_mcp.models.knowledge_item import KnowledgeItem


def summarize(content: str) -> str:
    lines = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#")]
    return " ".join(lines[:3])[:300]


def flatten_versions(versions: dict[str, Any]) -> list[str]:
    flattened: list[str] = []
    for value in versions.values():
        if isinstance(value, list):
            flattened.extend(str(entry) for entry in value)
    return flattened


def extract_steps(content: str) -> list[str]:
    result = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            result.append(stripped[2:].strip())
        elif stripped[:2] in ("1.", "2.", "3."):
            result.append(stripped[2:].strip())
        if len(result) == 5:
            break
    return result


def extract_fix(content: str) -> str:
    for marker in ["最终修复", "最终方案", "解决方案"]:
        if marker in content:
            section = content.split(marker, 1)[1]
            return summarize(section)
    return summarize(content)


def build_source_entry(item: KnowledgeItem) -> dict[str, str]:
    return {"id": item.id, "title": item.title, "type": item.category, "path": item.path}
