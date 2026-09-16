from __future__ import annotations

from pathlib import Path

from knowledge_agent_mcp.application import build_application
from knowledge_agent_mcp.models import ConsultKnowledgeRequest, SearchKnowledgeRequest


def test_index_builds_and_search_returns_solution() -> None:
    app = build_application(Path(__file__).resolve().parents[1])
    result = app._search_knowledge(
        SearchKnowledgeRequest(
            query="MCP knowledge retrieval SQLite",
            categories=["solution", "best_practice", "ai"],
            top_k=5,
        )
    )
    assert result["results"]
    assert any(item["category"] == "solution" for item in result["results"])


def test_consult_knowledge_returns_agent_configuration() -> None:
    app = build_application(Path(__file__).resolve().parents[1])
    request = ConsultKnowledgeRequest(
        task="设计一个只读知识检索 MCP 服务",
        stage="planning",
        max_results=5,
    )
    result = app._consult_knowledge(request, "test-request")
    assert result["agent_configuration"]
    assert result["task_understanding"]["stage"] == "planning"
