from __future__ import annotations

import asyncio

from mcp.types import CallToolRequest, CallToolRequestParams, ListToolsRequest

from knowledge_agent_mcp.application import build_application
from knowledge_agent_mcp.models import SearchKnowledgeRequest
from knowledge_agent_mcp.server import create_server


def test_server_registers_mcp_handlers() -> None:
    server = create_server()

    assert ListToolsRequest in server.request_handlers
    assert CallToolRequest in server.request_handlers


def test_server_handles_search_request() -> None:
    server = create_server()
    request = CallToolRequest(
        params=CallToolRequestParams(
            name="search_knowledge",
            arguments={"query": "MCP", "top_k": 1},
        )
    )

    result = asyncio.run(server.request_handlers[CallToolRequest](request))

    assert result.root.content
    assert result.root.content[0].type == "text"


def test_search_supports_chinese_and_rejects_unrelated_queries() -> None:
    app = build_application()

    chinese = app._search_knowledge(SearchKnowledgeRequest(query="语义分割", top_k=3))
    unrelated = app._search_knowledge(SearchKnowledgeRequest(query="无关内容xyz", top_k=3))

    assert chinese["results"]
    assert unrelated["results"] == []
