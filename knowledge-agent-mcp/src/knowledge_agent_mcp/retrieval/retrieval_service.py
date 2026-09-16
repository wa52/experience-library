from __future__ import annotations

from typing import Any

from knowledge_agent_mcp.repositories.knowledge_repository import KnowledgeRepository
from knowledge_agent_mcp.retrieval.context_builder import flatten_versions
from knowledge_agent_mcp.retrieval.keyword_search import keyword_score, tokenize
from knowledge_agent_mcp.retrieval.metadata_filter import apply_filters
from knowledge_agent_mcp.retrieval.vector_search import (
    domain_score,
    freshness_score,
    vector_score,
)

STATUS_SCORES = {"verified": 1.0, "reviewed": 0.85, "draft": 0.6, "deprecated": 0.3, "archived": 0.2}


class RetrievalService:
    def __init__(self, repository: KnowledgeRepository, weights: dict[str, float] | None = None) -> None:
        self.repository = repository
        self.weights = weights or {
            "keyword": 0.30,
            "vector": 0.30,
            "category": 0.15,
            "domain": 0.10,
            "version": 0.08,
            "status_confidence": 0.05,
            "freshness": 0.02,
        }

    def search(self, query: str, filters: dict[str, Any] | None = None, top_k: int = 10) -> list[dict[str, Any]]:
        query_tokens = tokenize(query)
        candidate_ids = self.repository.search_ids(query, limit=max(top_k * 20, 100))
        if not candidate_ids:
            return []
        items_by_id = {item.id: item for item in self.repository.items_by_ids(candidate_ids)}
        all_items = [items_by_id[item_id] for item_id in candidate_ids if item_id in items_by_id]
        filtered = apply_filters(all_items, filters or {})

        scored = []
        for item in filtered:
            kw_score = keyword_score(query_tokens, item)
            vec_score = vector_score(query_tokens, item)
            cat_score = 1.0 if not filters or not filters.get("categories") or item.category in filters["categories"] else 0.0
            dom_score = domain_score(query_tokens, item.domain)
            flat_versions = {v.lower() for row in item.versions.values() for v in (row if isinstance(row, list) else [row])}
            ver_score = 1.0 if not filters or not filters.get("versions") or flat_versions else 0.0
            sta_score = STATUS_SCORES.get(item.status, 0.5) * item.confidence
            fre_score = freshness_score(item.updated_at)

            total = (
                kw_score * self.weights.get("keyword", 0.30)
                + vec_score * self.weights.get("vector", 0.30)
                + cat_score * self.weights.get("category", 0.15)
                + dom_score * self.weights.get("domain", 0.10)
                + ver_score * self.weights.get("version", 0.08)
                + sta_score * self.weights.get("status_confidence", 0.05)
                + fre_score * self.weights.get("freshness", 0.02)
            )
            if total <= 0:
                continue
            scored.append({
                "id": item.id,
                "title": item.title,
                "category": item.category,
                "score": round(total, 4),
                "summary": item.summary,
                "path": item.path,
                "versions": flatten_versions(item.versions),
                "status": item.status,
            })

        scored.sort(key=lambda e: e["score"], reverse=True)
        return scored[:top_k]
