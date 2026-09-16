from __future__ import annotations

import re
import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from knowledge_agent_mcp.indexing.chunker import chunk_markdown
from knowledge_agent_mcp.indexing.markdown_parser import split_front_matter
from knowledge_agent_mcp.indexing.metadata_parser import parse_metadata
from knowledge_agent_mcp.models.knowledge_item import KnowledgeItem
from knowledge_agent_mcp.retrieval.context_builder import summarize
from knowledge_agent_mcp.retrieval.keyword_search import tokenize


class SQLiteKnowledgeRepository:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(self.database_path), timeout=30)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA busy_timeout=30000")

    def create_schema(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS knowledge_items (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                path TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL,
                knowledge_type TEXT NOT NULL,
                domain TEXT NOT NULL,
                summary TEXT NOT NULL,
                content TEXT NOT NULL,
                status TEXT NOT NULL,
                confidence REAL NOT NULL,
                created_at TEXT,
                updated_at TEXT,
                content_hash TEXT NOT NULL,
                file_mtime REAL NOT NULL,
                file_size INTEGER NOT NULL,
                metadata_json TEXT NOT NULL DEFAULT '{}'
            );
            CREATE TABLE IF NOT EXISTS knowledge_tags (
                knowledge_id TEXT NOT NULL,
                tag TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS knowledge_versions (
                knowledge_id TEXT NOT NULL,
                technology TEXT NOT NULL,
                version TEXT NOT NULL,
                version_type TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS knowledge_relations (
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                relation_type TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS knowledge_chunks (
                id TEXT PRIMARY KEY,
                knowledge_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                heading TEXT NOT NULL,
                content TEXT NOT NULL,
                token_count INTEGER NOT NULL,
                embedding_id TEXT
            );
            CREATE TABLE IF NOT EXISTS index_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(
                id UNINDEXED,
                title,
                summary,
                content,
                tags,
                tokenize='trigram'
            );
            CREATE INDEX IF NOT EXISTS idx_knowledge_items_category ON knowledge_items(category);
            CREATE INDEX IF NOT EXISTS idx_knowledge_items_status ON knowledge_items(status);
            CREATE INDEX IF NOT EXISTS idx_knowledge_tags_knowledge_id ON knowledge_tags(knowledge_id);
            CREATE INDEX IF NOT EXISTS idx_knowledge_tags_tag ON knowledge_tags(tag);
            CREATE INDEX IF NOT EXISTS idx_knowledge_versions_knowledge_id ON knowledge_versions(knowledge_id);
            CREATE INDEX IF NOT EXISTS idx_knowledge_versions_version ON knowledge_versions(version);
            CREATE INDEX IF NOT EXISTS idx_knowledge_relations_source_id ON knowledge_relations(source_id);
            CREATE INDEX IF NOT EXISTS idx_knowledge_relations_target_id ON knowledge_relations(target_id);
            CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_knowledge_id ON knowledge_chunks(knowledge_id);
            """
        )
        columns = {row[1] for row in self.connection.execute("PRAGMA table_info(knowledge_items)")}
        if "metadata_json" not in columns:
            self.connection.execute("ALTER TABLE knowledge_items ADD COLUMN metadata_json TEXT NOT NULL DEFAULT '{}'")
        fts_version = self.connection.execute(
            "SELECT value FROM index_metadata WHERE key = 'fts_version'"
        ).fetchone()
        fts_count = self.connection.execute("SELECT count(*) FROM knowledge_fts").fetchone()[0]
        item_count = self.connection.execute("SELECT count(*) FROM knowledge_items").fetchone()[0]
        if (not fts_version or fts_version[0] != "3") or fts_count != item_count:
            self.connection.execute("DROP TABLE IF EXISTS knowledge_fts")
            self.connection.execute(
                "CREATE VIRTUAL TABLE knowledge_fts USING fts5(id UNINDEXED, title, summary, content, tags, tokenize='trigram')"
            )
            self.connection.execute("DELETE FROM knowledge_fts")
            self.connection.execute(
                """
                INSERT INTO knowledge_fts(id, title, summary, content, tags)
                SELECT id, title, summary, content,
                       domain || ' ' || category || ' ' || knowledge_type || ' ' || metadata_json
                FROM knowledge_items
                """
            )
            self.connection.execute(
                "REPLACE INTO index_metadata(key, value, updated_at) VALUES('fts_version', '3', ?)",
                (self._now(),),
            )
        self.connection.commit()

    def upsert_item(
        self,
        item: KnowledgeItem,
        resolved_path: str,
        content_hash: str,
        file_mtime: float,
        file_size: int,
    ) -> None:
        existing = self.connection.execute(
            "SELECT id FROM knowledge_items WHERE path = ?", (resolved_path,)
        ).fetchone()
        if existing:
            self.delete_item(existing["id"])
        self.delete_item(item.id)
        self.connection.execute(
            """
            INSERT INTO knowledge_items(
                id, title, path, category, knowledge_type, domain, summary, content,
                status, confidence, created_at, updated_at, content_hash, file_mtime, file_size,
                metadata_json
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.id,
                item.title,
                resolved_path,
                item.category,
                item.knowledge_type,
                item.domain,
                item.summary,
                item.content,
                item.status,
                item.confidence,
                item.created_at,
                item.updated_at,
                content_hash,
                file_mtime,
                file_size,
                json.dumps(
                    {
                        "technologies": item.technologies,
                        "languages": item.languages,
                        "versions": item.versions,
                        "source_ids": item.source_ids,
                    },
                    ensure_ascii=False,
                ),
            ),
        )
        self.connection.execute("DELETE FROM knowledge_fts WHERE id = ?", (item.id,))
        self.connection.execute(
            "INSERT INTO knowledge_fts(id, title, summary, content, tags) VALUES(?, ?, ?, ?, ?)",
            (
                item.id,
                item.title,
                item.summary,
                item.content,
                " ".join(
                    item.tags
                    + item.technologies
                    + item.languages
                    + [
                        str(value)
                        for values in item.versions.values()
                        for value in (values if isinstance(values, list) else [values])
                    ]
                    + [item.domain, item.category, item.knowledge_type]
                ),
            ),
        )
        self.connection.executemany(
            "INSERT INTO knowledge_tags(knowledge_id, tag) VALUES(?, ?)",
            [(item.id, tag) for tag in item.tags],
        )
        version_rows = []
        for version_type, values in item.versions.items():
            if isinstance(values, list):
                for value in values:
                    for technology in item.technologies or [item.domain]:
                        version_rows.append((item.id, technology, str(value), str(version_type)))
        if version_rows:
            self.connection.executemany(
                "INSERT INTO knowledge_versions(knowledge_id, technology, version, version_type) VALUES(?, ?, ?, ?)",
                version_rows,
            )
        relation_rows = []
        for relation_type, target_ids in item.related_items.items():
            for target_id in target_ids:
                relation_rows.append((item.id, target_id, relation_type))
        if relation_rows:
            self.connection.executemany(
                "INSERT INTO knowledge_relations(source_id, target_id, relation_type) VALUES(?, ?, ?)",
                relation_rows,
            )
        chunk_rows = []
        for chunk_index, (heading, chunk_content) in enumerate(chunk_markdown(item.content)):
            chunk_rows.append(
                (
                    f"{item.id}:{chunk_index}",
                    item.id,
                    chunk_index,
                    heading,
                    chunk_content,
                    len(tokenize(chunk_content)),
                    None,
                )
            )
        if chunk_rows:
            self.connection.executemany(
                """
                INSERT INTO knowledge_chunks(id, knowledge_id, chunk_index, heading, content, token_count, embedding_id)
                VALUES(?, ?, ?, ?, ?, ?, ?)
                """,
                chunk_rows,
            )

    def delete_item(self, knowledge_id: str) -> None:
        self.connection.execute("DELETE FROM knowledge_fts WHERE id = ?", (knowledge_id,))
        for table, key in [
            ("knowledge_items", "id"),
            ("knowledge_tags", "knowledge_id"),
            ("knowledge_versions", "knowledge_id"),
            ("knowledge_relations", "source_id"),
            ("knowledge_chunks", "knowledge_id"),
        ]:
            self.connection.execute(f"DELETE FROM {table} WHERE {key} = ?", (knowledge_id,))
        self.connection.execute("DELETE FROM knowledge_relations WHERE target_id = ?", (knowledge_id,))

    def load_item_by_id(self, knowledge_id: str) -> KnowledgeItem:
        row = self.connection.execute("SELECT * FROM knowledge_items WHERE id = ?", (knowledge_id,)).fetchone()
        if not row:
            raise LookupError(f"Knowledge item not found: {knowledge_id}")
        return self._row_to_item(row)

    def relations_for(self, knowledge_id: str) -> list[dict[str, str]]:
        rows = self.connection.execute(
            "SELECT source_id, target_id, relation_type FROM knowledge_relations WHERE source_id = ?", (knowledge_id,)
        ).fetchall()
        return [dict(row) for row in rows]

    def source_stub(self, knowledge_id: str) -> dict[str, Any]:
        try:
            item = self.load_item_by_id(knowledge_id)
        except LookupError:
            return {"id": knowledge_id, "missing": True}
        return {"id": item.id, "title": item.title, "path": item.path, "type": item.category}

    def all_items(self) -> list[KnowledgeItem]:
        rows = self.connection.execute("SELECT * FROM knowledge_items WHERE 1=1").fetchall()
        return self._rows_to_items(rows)

    def items_by_ids(self, knowledge_ids: list[str]) -> list[KnowledgeItem]:
        if not knowledge_ids:
            return []
        placeholders = ",".join("?" for _ in knowledge_ids)
        rows = self.connection.execute(
            f"SELECT * FROM knowledge_items WHERE id IN ({placeholders})",
            knowledge_ids,
        ).fetchall()
        return self._rows_to_items(rows)

    def search_ids(self, query: str, limit: int = 100) -> list[str]:
        tokens = tokenize(query)
        if not tokens:
            return []
        fts_tokens = [token for token in tokens if len(token) >= 3]
        if not fts_tokens:
            return self._search_short_tokens(tokens, limit)
        match_query = " OR ".join(f'"{token.replace(chr(34), "")}"' for token in fts_tokens)
        rows = self.connection.execute(
            "SELECT id FROM knowledge_fts WHERE knowledge_fts MATCH ? ORDER BY bm25(knowledge_fts) LIMIT ?",
            (match_query, limit),
        ).fetchall()
        return [row["id"] for row in rows]

    def _search_short_tokens(self, tokens: list[str], limit: int) -> list[str]:
        clauses = " OR ".join(
            "title LIKE ? OR summary LIKE ? OR content LIKE ? OR tags LIKE ?"
            for _ in tokens
        )
        values = [value for token in tokens for value in (f"%{token}%",) * 4]
        rows = self.connection.execute(
            f"SELECT id FROM knowledge_fts WHERE {clauses} LIMIT ?",
            (*values, limit),
        ).fetchall()
        return [row["id"] for row in rows]

    def get_indexed_paths(self) -> dict[str, dict[str, Any]]:
        return {
            row["path"]: dict(row)
            for row in self.connection.execute("SELECT path, content_hash, file_mtime, file_size FROM knowledge_items")
        }

    def update_index_metadata(self, key: str, value: str) -> None:
        self.connection.execute(
            "REPLACE INTO index_metadata(key, value, updated_at) VALUES(?, ?, ?)",
            (key, value, self._now()),
        )

    def commit(self) -> None:
        self.connection.commit()

    def query_stale_ids(self, stale_paths: list[str]) -> list[str]:
        ids = []
        for path in stale_paths:
            row = self.connection.execute("SELECT id FROM knowledge_items WHERE path = ?", (path,)).fetchone()
            if row:
                ids.append(row["id"])
        return ids

    def _row_to_item(self, row: sqlite3.Row) -> KnowledgeItem:
        return self._rows_to_items([row])[0]

    def _rows_to_items(self, rows: list[sqlite3.Row]) -> list[KnowledgeItem]:
        if not rows:
            return []
        item_ids = [row["id"] for row in rows]
        placeholders = ",".join("?" for _ in item_ids)
        tags_by_id: dict[str, list[str]] = {item_id: [] for item_id in item_ids}
        for tag_row in self.connection.execute(
            f"SELECT knowledge_id, tag FROM knowledge_tags WHERE knowledge_id IN ({placeholders})", item_ids
        ):
            tags_by_id[tag_row["knowledge_id"]].append(tag_row["tag"])
        versions_by_id: dict[str, dict[str, list[str]]] = {item_id: {} for item_id in item_ids}
        for version_row in self.connection.execute(
            f"SELECT knowledge_id, technology, version, version_type FROM knowledge_versions WHERE knowledge_id IN ({placeholders})",
            item_ids,
        ):
            versions_by_id[version_row["knowledge_id"]].setdefault(version_row["version_type"], []).append(version_row["version"])
        relations_by_id: dict[str, dict[str, list[str]]] = {item_id: {} for item_id in item_ids}
        for relation_row in self.connection.execute(
            f"SELECT source_id, target_id, relation_type FROM knowledge_relations WHERE source_id IN ({placeholders})",
            item_ids,
        ):
            relations_by_id[relation_row["source_id"]].setdefault(relation_row["relation_type"], []).append(relation_row["target_id"])
        items = []
        for row in rows:
            metadata = json.loads(row["metadata_json"] or "{}")
            tags = tags_by_id[row["id"]]
            items.append(KnowledgeItem(
                id=row["id"],
                title=row["title"],
                path=row["path"],
                category=row["category"],
                knowledge_type=row["knowledge_type"],
                domain=row["domain"],
                summary=row["summary"],
                content=row["content"],
                status=row["status"],
                confidence=row["confidence"],
                tags=tags,
                technologies=metadata.get("technologies") or self._extract_technologies(row["domain"], tags),
                languages=metadata.get("languages", []),
                versions=metadata.get("versions") or versions_by_id[row["id"]],
                related_items=relations_by_id[row["id"]],
                source_ids=metadata.get("source_ids", []),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            ))
        return items

    @staticmethod
    def _extract_technologies(domain: str, tags: list[str]) -> list[str]:
        parts = [part for part in re.split(r"[/_\-]", domain) if part]
        return list(dict.fromkeys(tags + parts[:2]))

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    @staticmethod
    def parse_knowledge_file(path: Path, raw_text: str) -> KnowledgeItem:
        front_matter, content = split_front_matter(raw_text)
        metadata = parse_metadata(front_matter) if front_matter else {}
        if "id" not in metadata or "title" not in metadata or "category" not in metadata:
            raise ValueError(f"Invalid knowledge file: {path}")
        summary = summarize(content)
        payload = {
            "id": metadata["id"],
            "title": metadata["title"],
            "path": str(path),
            "category": metadata["category"],
            "knowledge_type": metadata.get("knowledge_type", metadata["category"]),
            "domain": metadata.get("domain", "general"),
            "summary": summary,
            "content": content.strip(),
            "status": metadata.get("status", "draft"),
            "confidence": metadata.get("confidence", 0.5),
            "tags": metadata.get("tags", []),
            "technologies": metadata.get("technologies", []),
            "languages": metadata.get("languages", []),
            "versions": metadata.get("versions", {}),
            "related_items": metadata.get("related_items", {}),
            "source_ids": metadata.get("source_ids", []),
            "created_at": SQLiteKnowledgeRepository._normalize_scalar(metadata.get("created_at")),
            "updated_at": SQLiteKnowledgeRepository._normalize_scalar(metadata.get("updated_at")),
        }
        return KnowledgeItem.model_validate(payload)

    @staticmethod
    def _normalize_scalar(value: Any) -> Any:
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return value
