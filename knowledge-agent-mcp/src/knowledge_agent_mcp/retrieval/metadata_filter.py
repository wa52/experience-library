from __future__ import annotations

from typing import Any

from knowledge_agent_mcp.models.knowledge_item import KnowledgeItem


def filter_by_categories(items: list[KnowledgeItem], categories: list[str] | None) -> list[KnowledgeItem]:
    if not categories:
        return items
    return [item for item in items if item.category in categories]


def filter_by_technologies(items: list[KnowledgeItem], technologies: list[str] | None) -> list[KnowledgeItem]:
    if not technologies:
        return items
    tech_lower = {t.lower() for t in technologies}
    return [
        item for item in items
        if tech_lower.intersection({v.lower() for v in item.technologies})
    ]


def filter_by_status(items: list[KnowledgeItem], status: list[str] | None) -> list[KnowledgeItem]:
    if not status:
        return items
    return [item for item in items if item.status in status]


def filter_by_versions(items: list[KnowledgeItem], versions: list[str] | None) -> list[KnowledgeItem]:
    if not versions:
        return items
    version_lower = {v.lower() for v in versions}
    result = []
    for item in items:
        flat = {v.lower() for row in item.versions.values() for v in (row if isinstance(row, list) else [row])}
        if version_lower.intersection(flat):
            result.append(item)
    return result


def apply_filters(items: list[KnowledgeItem], filters: dict[str, Any]) -> list[KnowledgeItem]:
    result = list(items)
    result = filter_by_categories(result, filters.get("categories"))
    result = filter_by_technologies(result, filters.get("technologies"))
    result = filter_by_status(result, filters.get("status"))
    result = filter_by_versions(result, filters.get("versions"))
    return result
