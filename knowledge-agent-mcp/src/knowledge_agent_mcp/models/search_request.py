from __future__ import annotations

from pydantic import BaseModel, Field


class SearchKnowledgeRequest(BaseModel):
    query: str
    categories: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    versions: list[str] = Field(default_factory=list)
    status: list[str] = Field(default_factory=list)
    top_k: int = 10


class GetKnowledgeItemRequest(BaseModel):
    knowledge_id: str
    include_content: bool = True
    include_relations: bool = True
    include_sources: bool = True


class GetRelatedKnowledgeRequest(BaseModel):
    knowledge_id: str
    relation_types: list[str] = Field(default_factory=list)
    max_depth: int = 1
