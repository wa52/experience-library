from __future__ import annotations

from pathlib import Path

from knowledge_agent_mcp.core import KnowledgeApplication


def build_application(base_path: Path | None = None) -> KnowledgeApplication:
    root = base_path or Path(__file__).resolve().parents[2]
    return KnowledgeApplication(root)
