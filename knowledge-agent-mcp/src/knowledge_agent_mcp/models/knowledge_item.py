from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class KnowledgeItem(BaseModel):
    id: str
    title: str
    path: str
    category: str
    knowledge_type: str = "fact"
    domain: str = "general"
    summary: str = ""
    content: str = ""
    status: str = "draft"
    confidence: float = 0.5
    tags: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    versions: dict[str, Any] = Field(default_factory=dict)
    related_items: dict[str, list[str]] = Field(default_factory=dict)
    source_ids: list[str] = Field(default_factory=list)
    created_at: str | None = None
    updated_at: str | None = None
