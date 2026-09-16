from __future__ import annotations

import math
from collections import Counter
from datetime import datetime, timezone

from knowledge_agent_mcp.indexing.embedding_builder import TfidfEmbedding, get_embedding_model
from knowledge_agent_mcp.models.knowledge_item import KnowledgeItem
from knowledge_agent_mcp.retrieval.keyword_search import tokenize


def vector_score(query_tokens: list[str], item: KnowledgeItem) -> float:
    model = get_embedding_model()
    if model.fitted():
        query_vec = model.embed(" ".join(query_tokens))
        item_text = " ".join([item.title, item.summary or "", item.content[:4000]])
        item_vec = model.embed(item_text)
        return model.cosine_similarity(query_vec, item_vec)

    query_vector = Counter(query_tokens)
    item_vector = Counter(tokenize(" ".join([item.title, item.summary or "", item.content[:4000]])))
    dot = sum(query_vector[t] * item_vector[t] for t in query_vector)
    query_norm = math.sqrt(sum(v * v for v in query_vector.values()))
    item_norm = math.sqrt(sum(v * v for v in item_vector.values()))
    if not query_norm or not item_norm:
        return 0.0
    return dot / (query_norm * item_norm)


def domain_score(query_tokens: list[str], domain: str) -> float:
    domain_tokens = set(tokenize(domain))
    if not domain_tokens:
        return 0.0
    return sum(1 for t in query_tokens if t in domain_tokens) / max(len(query_tokens), 1)


def freshness_score(updated_at: str | None) -> float:
    if not updated_at:
        return 0.3
    try:
        updated = datetime.fromisoformat(updated_at)
    except ValueError:
        return 0.3
    age_days = max((datetime.now(timezone.utc).date() - updated.date()).days, 0)
    return max(0.0, min(1.0, 1 - age_days / 3650))
