from __future__ import annotations

from typing import Any

import yaml


def parse_metadata(raw_front_matter: str) -> dict[str, Any]:
    return yaml.safe_load(raw_front_matter) or {}
