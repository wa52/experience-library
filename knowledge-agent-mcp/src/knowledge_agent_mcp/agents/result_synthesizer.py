from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from knowledge_agent_mcp.llm.client import LLMClient

SYNTHESIS_PROMPT = """You are a knowledge synthesis assistant. Given knowledge items retrieved for a task, produce a concise structured summary.

Task: {task}
Stage: {stage}

Items:
{items}

Return a JSON object with:
- "summary": a 2-3 sentence overall summary
- "key_facts": array of key factual statements (max 5)
- "relevant_solutions": array of solution titles that apply (max 3)
- "identified_gaps": array of missing information notes (max 3)"""


@dataclass(slots=True)
class ResultSynthesizer:
    llm_client: LLMClient | None = None

    def synthesize(self, task: str, stage: str, items: list[dict[str, Any]]) -> dict[str, Any]:
        if self.llm_client is not None and items:
            try:
                items_text = "\n".join(
                    f"- {i.get('id', '')}: {i.get('title', '')} [{i.get('category', '')}] score={i.get('score', 0)}"
                    for i in items[:10]
                )
                prompt = SYNTHESIS_PROMPT.format(task=task, stage=stage, items=items_text)
                result = self.llm_client.generate_structured(
                    prompt,
                    {
                        "type": "object",
                        "properties": {
                            "summary": {"type": "string"},
                            "key_facts": {"type": "array", "items": {"type": "string"}},
                            "relevant_solutions": {"type": "array", "items": {"type": "string"}},
                            "identified_gaps": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                )
                return result
            except RuntimeError:
                pass
        return {}

    def build_source_entry(self, item_id: str, title: str, category: str, path: str) -> dict[str, str]:
        return {"id": item_id, "title": title, "type": category, "path": path}
