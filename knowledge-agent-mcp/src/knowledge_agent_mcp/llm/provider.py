from __future__ import annotations

from knowledge_agent_mcp.llm.client import LLMClient
from knowledge_agent_mcp.settings import LLMSettings


def get_llm_client(settings: LLMSettings | None = None) -> LLMClient:
    if settings is None:
        return LLMClient()
    return LLMClient(
        api_key=settings.api_key,
        base_url=settings.base_url,
        model=settings.model,
        temperature=settings.temperature,
        timeout_seconds=settings.timeout_seconds,
        max_retries=settings.max_retries,
    )
