from __future__ import annotations

from pathlib import Path

from knowledge_agent_mcp.application import build_application


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    app = build_application(root)
    rows = app.connection.execute(
        "SELECT category, COUNT(*) AS count FROM knowledge_items GROUP BY category ORDER BY category"
    ).fetchall()
    for row in rows:
        print(f"{row['category']}: {row['count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
