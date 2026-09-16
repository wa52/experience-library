from __future__ import annotations

from pydantic import BaseModel, Field


class ProjectContext(BaseModel):
    project_name: str | None = None
    languages: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    versions: dict[str, str] = Field(default_factory=dict)
    platform: str | None = None
    existing_modules: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


class ConsultKnowledgeRequest(BaseModel):
    task: str
    stage: str = "implementation"
    project_context: ProjectContext = Field(default_factory=ProjectContext)
    error_context: str | None = None
    max_results: int = 10
