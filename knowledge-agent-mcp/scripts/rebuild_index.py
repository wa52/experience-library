from __future__ import annotations

from pathlib import Path

from knowledge_agent_mcp.application import build_application


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    app = build_application(root)
    count = app.connection.execute("SELECT COUNT(*) FROM knowledge_items").fetchone()[0]
    print(f"Indexed knowledge items: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
