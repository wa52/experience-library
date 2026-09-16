from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from knowledge_agent_mcp.llm.client import LLMClient
from knowledge_agent_mcp.models import ConsultKnowledgeRequest

QUERY_HINTS = {
    "planning": ["solution", "project_experience", "best_practice", "technology", "code_example"],
    "implementation": ["technology", "code_example", "solution", "foundation"],
    "debugging": ["bug", "solution", "project_experience", "technology", "code_example"],
    "acceptance": ["best_practice", "project_experience", "solution"],
}

QUERY_EXPANSION_PROMPT = """You are a query planner for a knowledge retrieval system. Given a task description and context, generate up to {max_queries} specific search queries that would help find relevant knowledge.

Task: {task}
Stage: {stage}
Error context: {error_context}
Technologies: {technologies}

Return a JSON object with a "queries" field containing an array of query strings. Each query should target a different aspect of the task."""


@dataclass(slots=True)
class QueryPlanner:
    max_queries_per_round: int
    llm_client: LLMClient | None = None

    def build_plan(self, request: ConsultKnowledgeRequest, queries: list[str]) -> dict[str, object]:
        stage = request.stage.lower()
        return {
            "queries": queries[: self.max_queries_per_round],
            "knowledge_types": QUERY_HINTS.get(stage, QUERY_HINTS["implementation"]),
            "filters": {
                "technologies": request.project_context.technologies,
                "versions": list(request.project_context.versions.values()),
            },
        }

    def expand_queries(self, request: ConsultKnowledgeRequest, terms: list[str]) -> list[str]:
        if self.llm_client is not None:
            try:
                prompt = QUERY_EXPANSION_PROMPT.format(
                    max_queries=self.max_queries_per_round,
                    task=request.task,
                    stage=request.stage,
                    error_context=request.error_context or "none",
                    technologies=", ".join(request.project_context.technologies) or "general",
                )
                result = self.llm_client.generate_structured(
                    prompt,
                    {"type": "object", "properties": {"queries": {"type": "array", "items": {"type": "string"}}}},
                )
                expanded = result.get("queries", [])
                if expanded:
                    return expanded[: self.max_queries_per_round]
            except RuntimeError:
                pass
        base = " ".join(term for term in terms if term)
        expansions = [base]
        lower = base.lower()
        if "halcon" in lower:
            expansions.extend([f"{base} shape_model find_shape_model", f"{base} 标准流程 常见问题"])
        if any(word in lower for word in ["error", "失败", "bug", "异常"]):
            expansions.append(f"{base} 根本原因 最终修复")
        if "mcp" in lower or "agent" in lower:
            expansions.append(f"{base} tool resource stdio")
        return list(dict.fromkeys(q.strip() for q in expansions if q.strip()))[: self.max_queries_per_round]
