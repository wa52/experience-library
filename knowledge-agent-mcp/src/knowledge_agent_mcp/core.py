from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from knowledge_agent_mcp.agents.registry import load_agent_registry
from knowledge_agent_mcp.indexing import IndexBuilder
from knowledge_agent_mcp.logging import get_logger
from knowledge_agent_mcp.mcp_compat import types
from knowledge_agent_mcp.models import ConsultKnowledgeRequest, GetKnowledgeItemRequest, GetRelatedKnowledgeRequest, SearchKnowledgeRequest
from knowledge_agent_mcp.repositories.sqlite_repository import SQLiteKnowledgeRepository
from knowledge_agent_mcp.retrieval import RetrievalService
from knowledge_agent_mcp.retrieval.context_builder import extract_fix, extract_steps, flatten_versions, summarize
from knowledge_agent_mcp.settings import Settings

LOGGER = get_logger("knowledge_agent_mcp")

TOOL_SCHEMAS: dict[str, dict[str, Any]] = {
    "consult_knowledge": {
        "type": "object",
        "required": ["task"],
        "properties": {
            "task": {"type": "string"},
            "stage": {"type": "string"},
            "project_context": {"type": "object"},
            "error_context": {"type": ["string", "null"]},
            "max_results": {"type": "integer", "minimum": 1, "maximum": 30},
        },
    },
    "search_knowledge": {
        "type": "object",
        "required": ["query"],
        "properties": {
            "query": {"type": "string"},
            "categories": {"type": "array", "items": {"type": "string"}},
            "technologies": {"type": "array", "items": {"type": "string"}},
            "versions": {"type": "array", "items": {"type": "string"}},
            "status": {"type": "array", "items": {"type": "string"}},
            "top_k": {"type": "integer", "minimum": 1, "maximum": 30},
        },
    },
    "get_knowledge_item": {
        "type": "object",
        "required": ["knowledge_id"],
        "properties": {
            "knowledge_id": {"type": "string"},
            "include_content": {"type": "boolean"},
            "include_relations": {"type": "boolean"},
            "include_sources": {"type": "boolean"},
        },
    },
    "get_related_knowledge": {
        "type": "object",
        "required": ["knowledge_id"],
        "properties": {
            "knowledge_id": {"type": "string"},
            "relation_types": {"type": "array", "items": {"type": "string"}},
            "max_depth": {"type": "integer", "minimum": 1, "maximum": 1},
        },
    },
}

QUERY_HINTS = {
    "planning": ["solution", "project_experience", "best_practice", "technology", "code_example"],
    "implementation": ["technology", "code_example", "solution", "foundation"],
    "debugging": ["bug", "solution", "project_experience", "technology", "code_example"],
    "acceptance": ["best_practice", "project_experience", "solution"],
}


class KnowledgeApplication:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.settings = Settings.load(root)
        self.agent_registry = load_agent_registry(root)
        self.knowledge_base = (root / self.settings.knowledge_base_path).resolve()
        database_path = (root / self.settings.database_path).resolve()
        self.repository = SQLiteKnowledgeRepository(database_path)
        self.repository.create_schema()
        self.retrieval_service = RetrievalService(
            self.repository,
            self.settings.retrieval.ranking_weights.model_dump() if hasattr(self.settings.retrieval.ranking_weights, "model_dump") else {},
        )
        self.index_builder = IndexBuilder(self.repository)
        self._sync_index()

    def list_tools(self) -> types.ListToolsResult:
        return types.ListToolsResult(
                tools=[
                    types.Tool(
                        name=name,
                        title=name,
                        description=self._tool_description(name),
                        inputSchema=schema,
                    )
                for name, schema in TOOL_SCHEMAS.items()
            ]
        )

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> types.CallToolResult:
        request_id = str(uuid.uuid4())
        LOGGER.info("tool_call_start request_id=%s tool=%s", request_id, name)
        try:
            if name == "consult_knowledge":
                payload = self._consult_knowledge(ConsultKnowledgeRequest.model_validate(arguments), request_id)
            elif name == "search_knowledge":
                payload = self._search_knowledge(SearchKnowledgeRequest.model_validate(arguments))
            elif name == "get_knowledge_item":
                payload = self._get_knowledge_item(GetKnowledgeItemRequest.model_validate(arguments))
            elif name == "get_related_knowledge":
                payload = self._get_related_knowledge(GetRelatedKnowledgeRequest.model_validate(arguments))
            else:
                return self._error_result("INVALID_REQUEST", f"Unknown tool: {name}", True)
        except ValidationError as exc:
            return self._error_result("INVALID_REQUEST", exc.errors()[0]["msg"], True)
        except FileNotFoundError:
            return self._error_result("KB_NOT_FOUND", "Knowledge base path does not exist", True)
        except LookupError as exc:
            return self._error_result("KNOWLEDGE_ITEM_NOT_FOUND", str(exc), True)

        payload["request_id"] = payload.get("request_id", request_id)
        LOGGER.info("tool_call_done request_id=%s tool=%s returned_keys=%s", request_id, name, sorted(payload.keys()))
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, indent=2))]
        )

    def _consult_knowledge(self, request: ConsultKnowledgeRequest, request_id: str) -> dict[str, Any]:
        stage = request.stage.lower()
        LOGGER.info("consult_start request_id=%s stage=%s task=%s", request_id, stage, request.task[:120])
        terms = [request.task]
        if request.error_context:
            terms.append(request.error_context)
        terms.extend(request.project_context.technologies)
        terms.extend(request.project_context.languages)
        terms.extend(request.project_context.constraints)

        understanding = {
            "task_type": self._infer_task_type(request.task, request.error_context),
            "stage": stage,
            "domains": request.project_context.technologies or self._guess_domains(request.task),
            "languages": request.project_context.languages,
            "versions": request.project_context.versions,
            "constraints": request.project_context.constraints,
        }

        plan = {
            "queries": self._expand_queries(terms)[: self.settings.agent.max_queries_per_round],
            "knowledge_types": QUERY_HINTS.get(stage, QUERY_HINTS["implementation"]),
            "filters": {
                "technologies": request.project_context.technologies,
                "versions": list(request.project_context.versions.values()),
            },
        }

        merged: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        for query in plan["queries"]:
            LOGGER.info("consult_query request_id=%s query=%s", request_id, query[:160])
            results = self._search_knowledge(
                SearchKnowledgeRequest(
                    query=query,
                    categories=plan["knowledge_types"],
                    technologies=request.project_context.technologies,
                    versions=list(request.project_context.versions.values()),
                    status=["verified", "reviewed", "draft"],
                    top_k=min(request.max_results, self.settings.agent.max_results_per_query),
                )
            )["results"]
            for result in results:
                if result["id"] not in seen_ids:
                    seen_ids.add(result["id"])
                    merged.append(result)

        selected = merged[: request.max_results]
        selected = self._ensure_category_coverage(
            selected=selected,
            request=request,
            plan=plan,
        )
        facts = []
        recommended_solutions = []
        similar_projects = []
        known_bugs = []
        code_examples = []
        best_practices = []
        version_notes = []
        test_requirements = []
        risks = []
        sources = []

        for result in selected:
            item = self.repository.load_item_by_id(result["id"])
            sources.append({"id": item.id, "title": item.title, "type": item.category, "path": item.path})
            summary = item.summary or summarize(item.content)
            if item.category in {"technology", "foundation", "ai"}:
                facts.append({"fact": summary, "confidence": item.confidence, "source_id": item.id})
            if item.category == "solution":
                recommended_solutions.append(
                    {
                        "title": item.title,
                        "summary": summary,
                        "applicability": item.domain,
                        "steps": extract_steps(item.content),
                        "limitations": [],
                        "source_ids": [item.id],
                    }
                )
            if item.category == "project_experience":
                similar_projects.append(
                    {
                        "project": item.title,
                        "similarity_reason": item.domain,
                        "reusable_parts": item.tags[:3],
                        "lessons": [summary],
                        "source_id": item.id,
                    }
                )
            if item.category == "bug":
                known_bugs.append(
                    {
                        "symptom": item.title,
                        "cause": summary,
                        "solution": extract_fix(item.content),
                        "applicable_versions": flatten_versions(item.versions),
                        "source_id": item.id,
                    }
                )
            if item.category == "code_example":
                code_examples.append(
                    {
                        "title": item.title,
                        "language": item.languages[0] if item.languages else "unknown",
                        "version": flatten_versions(item.versions),
                        "test_status": item.status,
                        "knowledge_id": item.id,
                    }
                )
            if item.category == "best_practice":
                best_practices.append(
                    {
                        "rule": item.title,
                        "reason": summary,
                        "applicability": item.domain,
                        "source_id": item.id,
                    }
                )
            if item.versions:
                version_notes.append(
                    {
                        "technology": ", ".join(item.technologies) or item.domain,
                        "version": flatten_versions(item.versions),
                        "note": summary,
                        "source_id": item.id,
                    }
                )
            if item.category in {"solution", "best_practice", "project_experience"}:
                test_requirements.append(
                    {"requirement": f"Verify {item.title}", "reason": item.category, "source_id": item.id}
                )
            if item.status != "verified" or item.confidence < 0.8:
                risks.append(
                    {
                        "risk": f"{item.title} is not strongly verified",
                        "severity": "medium",
                        "mitigation": "Cross-check against source or project validation.",
                    }
                )

        return {
            "request_id": request_id,
            "agent_configuration": self.agent_registry,
            "task_understanding": understanding,
            "retrieval_plan": plan,
            "technical_facts": facts,
            "recommended_solutions": recommended_solutions,
            "similar_projects": similar_projects,
            "known_bugs": known_bugs,
            "code_examples": code_examples,
            "best_practices": best_practices,
            "version_notes": version_notes,
            "test_requirements": test_requirements,
            "risks": risks,
            "knowledge_gaps": self._knowledge_gaps(request, selected),
            "sources": sources,
            "partial_result": len(merged) > request.max_results,
            "agent_degraded": True,
        }

    def _search_knowledge(self, request: SearchKnowledgeRequest) -> dict[str, Any]:
        top_k = min(request.top_k, self.settings.retrieval.max_top_k)
        LOGGER.info(
            "search_start query=%s categories=%s technologies=%s versions=%s top_k=%s",
            request.query[:160],
            request.categories,
            request.technologies,
            request.versions,
            top_k,
        )
        filters = {
            "categories": request.categories,
            "technologies": request.technologies,
            "versions": request.versions,
            "status": request.status,
        }
        results = self.retrieval_service.search(request.query, filters, top_k)
        LOGGER.info("search_done query=%s result_count=%s", request.query[:120], len(results))
        return {"results": results}

    def _get_knowledge_item(self, request: GetKnowledgeItemRequest) -> dict[str, Any]:
        item = self.repository.load_item_by_id(request.knowledge_id)
        payload: dict[str, Any] = item.model_dump()
        if not request.include_content:
            payload.pop("content", None)
        if request.include_relations:
            payload["relations"] = self.repository.relations_for(item.id)
        if request.include_sources:
            payload["sources"] = [self.repository.source_stub(source_id) for source_id in item.source_ids]
        return payload

    def _get_related_knowledge(self, request: GetRelatedKnowledgeRequest) -> dict[str, Any]:
        if request.max_depth != 1:
            return self._error_payload("INVALID_REQUEST", "Only max_depth=1 is supported", True)
        relations = self.repository.relations_for(request.knowledge_id)
        related = []
        for relation in relations:
            if request.relation_types and relation["relation_type"] not in request.relation_types:
                continue
            try:
                item = self.repository.load_item_by_id(relation["target_id"])
            except LookupError:
                continue
            related.append(
                {
                    "relation_type": relation["relation_type"],
                    "knowledge": {
                        "id": item.id,
                        "title": item.title,
                        "category": item.category,
                        "path": item.path,
                    },
                }
            )
        return {"knowledge_id": request.knowledge_id, "related_items": related}

    def _sync_index(self) -> None:
        self.index_builder.sync_index(self.knowledge_base)

    def _expand_queries(self, terms: list[str]) -> list[str]:
        base = " ".join(term for term in terms if term)
        expansions = [base]
        lower = base.lower()
        if "halcon" in lower:
            expansions.extend([f"{base} shape_model find_shape_model", f"{base} 标准流程 常见问题"])
        if any(word in lower for word in ["error", "失败", "bug", "异常"]):
            expansions.append(f"{base} 根本原因 最终修复")
        if "mcp" in lower or "agent" in lower:
            expansions.append(f"{base} tool resource stdio")
        return list(dict.fromkeys(query.strip() for query in expansions if query.strip()))

    def _infer_task_type(self, task: str, error_context: str | None) -> str:
        text = f"{task} {error_context or ''}".lower()
        if error_context or any(token in text for token in ["error", "bug", "异常", "失败"]):
            return "debugging"
        if any(token in text for token in ["设计", "规划", "architecture", "plan"]):
            return "planning"
        if any(token in text for token in ["验收", "test", "验证"]):
            return "acceptance"
        return "implementation"

    def _guess_domains(self, task: str) -> list[str]:
        text = task.lower()
        domains = []
        for candidate in ["HALCON", "OpenCV", "FastAPI", "PySide6", "MCP", "RAG", "Agent"]:
            if candidate.lower() in text:
                domains.append(candidate)
        return domains or ["general"]

    def _knowledge_gaps(self, request: ConsultKnowledgeRequest, selected: list[dict[str, Any]]) -> list[dict[str, str]]:
        gaps = []
        if not selected:
            gaps.append({"missing_information": "No relevant knowledge matched the request", "impact": "high"})
        if not request.project_context.versions:
            gaps.append({"missing_information": "Technology version not provided", "impact": "medium"})
        if not request.project_context.technologies:
            gaps.append({"missing_information": "Technology scope not explicit", "impact": "medium"})
        return gaps

    def _ensure_category_coverage(
        self,
        selected: list[dict[str, Any]],
        request: ConsultKnowledgeRequest,
        plan: dict[str, Any],
    ) -> list[dict[str, Any]]:
        required_by_stage = {
            "planning": ["solution", "project_experience", "code_example", "technology"],
            "implementation": ["technology", "code_example", "solution"],
            "debugging": ["bug", "solution", "code_example"],
            "acceptance": ["best_practice", "solution"],
        }
        required = required_by_stage.get(request.stage.lower(), [])
        selected_categories = {item["category"] for item in selected}
        augmented = list(selected)

        for category in required:
            if category in selected_categories:
                continue
            supplemental_query = " ".join(
                [
                    request.task,
                    request.error_context or "",
                    *request.project_context.technologies,
                    *request.project_context.languages,
                ]
            )
            supplemental = self._search_knowledge(
                SearchKnowledgeRequest(
                    query=supplemental_query,
                    categories=[category],
                    technologies=request.project_context.technologies,
                    versions=list(request.project_context.versions.values()),
                    status=["verified", "reviewed", "draft", "tested"],
                    top_k=1,
                )
            )["results"]
            if not supplemental and request.project_context.versions:
                # Keep category and technology constraints, but allow reference
                # examples from another version when the exact version is absent.
                supplemental = self._search_knowledge(
                    SearchKnowledgeRequest(
                        query=supplemental_query,
                        categories=[category],
                        technologies=request.project_context.technologies,
                        status=["verified", "reviewed", "draft", "tested"],
                        top_k=1,
                    )
                )["results"]
            for result in supplemental:
                if result["id"] not in {entry["id"] for entry in augmented}:
                    augmented.append(result)
                    selected_categories.add(category)
                    break

        return augmented[: request.max_results]

    def _tool_description(self, name: str) -> str:
        return {
            "consult_knowledge": "High-level knowledge consultation that plans queries, retrieves relevant items, and returns a structured context package.",
            "search_knowledge": "Low-level precise search over the read-only knowledge base with metadata filters.",
            "get_knowledge_item": "Read one knowledge item with optional content, relations, and source references.",
            "get_related_knowledge": "Read first-order related knowledge items by relation type.",
        }[name]

    def _error_payload(self, code: str, message: str, recoverable: bool) -> dict[str, Any]:
        return {
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "recoverable": recoverable,
                "suggested_action": "Check request arguments or rebuild the knowledge index.",
            },
        }

    def _error_result(self, code: str, message: str, recoverable: bool) -> types.CallToolResult:
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=json.dumps(self._error_payload(code, message, recoverable), ensure_ascii=False, indent=2))],
            isError=True,
        )
