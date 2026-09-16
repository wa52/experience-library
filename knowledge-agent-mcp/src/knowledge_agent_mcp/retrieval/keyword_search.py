from __future__ import annotations

import re
from typing import Any

from knowledge_agent_mcp.models.knowledge_item import KnowledgeItem


def tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9_\-\u4e00-\u9fff]+", text.lower())


def keyword_score(query_tokens: list[str], item: KnowledgeItem) -> float:
    if not query_tokens:
        return 0.0
    haystack = set(tokenize(" ".join([item.title, item.summary, item.domain, " ".join(item.tags)])))
    matched = sum(1 for token in query_tokens if token in haystack)
    return matched / len(query_tokens)
