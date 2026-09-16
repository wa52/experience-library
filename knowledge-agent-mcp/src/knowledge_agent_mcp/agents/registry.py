from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_agent_registry(root: Path) -> dict[str, Any]:
    models_path = root / "config" / "models.yaml"
    workflow_path = root / "config" / "agent_workflow.yaml"

    models_data = yaml.safe_load(models_path.read_text(encoding="utf-8")) if models_path.exists() else {}
    workflow_data = yaml.safe_load(workflow_path.read_text(encoding="utf-8")) if workflow_path.exists() else {}

    return {
        "agent_models": (models_data or {}).get("agent_models", {}),
        "workflow": (workflow_data or {}).get("workflow", {}),
        "rules": (workflow_data or {}).get("rules", {}),
    }
