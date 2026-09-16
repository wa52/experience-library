from __future__ import annotations

from pathlib import Path

from knowledge_agent_mcp.application import build_application
from knowledge_agent_mcp.models import SearchKnowledgeRequest


def test_index_contains_many_knowledge_items() -> None:
    app = build_application(Path(__file__).resolve().parents[2])
    items = app.repository.all_items()
    assert len(items) >= 30


def test_search_can_find_label_studio_bug() -> None:
    app = build_application(Path(__file__).resolve().parents[2])
    result = app._search_knowledge(
        SearchKnowledgeRequest(
            query="No module named label_studio.__main__",
            categories=["bug", "solution", "project_experience"],
            technologies=["LabelStudio", "Python"],
            top_k=5,
        )
    )
    ids = [item["id"] for item in result["results"]]
    assert "bug-label-studio-main-missing" in ids
