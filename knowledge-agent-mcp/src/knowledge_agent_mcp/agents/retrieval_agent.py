from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from knowledge_agent_mcp.llm.client import LLMClient

RELEVANCE_PROMPT = """You are a retrieval relevance judge. Given a search query and a list of candidate knowledge items, identify which items are relevant and should be kept.

Query: {query}

Candidates:
{candidates}

Return a JSON object with a "relevant_ids" field containing an array of IDs (as strings) that are relevant to the query. Keep only truly relevant items."""


@dataclass(slots=True)
class RetrievalAgent:
    max_results_per_query: int
    llm_client: LLMClient | None = None

    def deduplicate_results(self, batches: list[list[dict[str, object]]], max_results: int) -> list[dict[str, object]]:
        merged: list[dict[str, object]] = []
        seen_ids: set[str] = set()
        for batch in batches:
            for result in batch[: self.max_results_per_query]:
                result_id = str(result["id"])
                if result_id in seen_ids:
                    continue
                seen_ids.add(result_id)
                merged.append(result)
                if len(merged) >= max_results:
                    return merged
        return merged

    def filter_relevant(self, query: str, candidates: list[dict[str, object]], top_k: int) -> list[dict[str, object]]:
        if self.llm_client is not None and candidates:
            try:
                items_text = "\n".join(
                    f"- ID: {c['id']}, Title: {c.get('title', '')}, Category: {c.get('category', '')}, Summary: {str(c.get('summary', ''))[:200]}"
                    for c in candidates
                )
                prompt = RELEVANCE_PROMPT.format(query=query, candidates=items_text)
                result = self.llm_client.generate_structured(
                    prompt,
                    {"type": "object", "properties": {"relevant_ids": {"type": "array", "items": {"type": "string"}}}},
                )
                relevant_ids = set(result.get("relevant_ids", []))
                if relevant_ids:
                    ordered = [c for c in candidates if str(c["id"]) in relevant_ids]
                    if ordered:
                        return ordered[:top_k]
            except RuntimeError:
                pass
        return candidates[:top_k]
