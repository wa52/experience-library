from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from knowledge_agent_mcp.indexing.embedding_builder import TfidfEmbedding, set_embedding_model
from knowledge_agent_mcp.indexing.scanner import scan_markdown_files
from knowledge_agent_mcp.repositories.knowledge_repository import KnowledgeRepository


class IndexBuilder:
    def __init__(self, repository: KnowledgeRepository) -> None:
        self.repository = repository
        self.embedding_model = TfidfEmbedding()

    def sync_index(self, knowledge_base_path: Path) -> int:
        if not knowledge_base_path.exists():
            raise FileNotFoundError(str(knowledge_base_path))

        files = scan_markdown_files(knowledge_base_path)
        current_paths = {str(path.resolve()) for path in files}
        indexed = self.repository.get_indexed_paths()

        for path in files:
            resolved = str(path.resolve())
            stat = path.stat()
            content = path.read_text(encoding="utf-8")
            content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
            stored = indexed.get(resolved)
            if stored and stored["content_hash"] == content_hash and stored["file_size"] == stat.st_size:
                continue
            item = self.repository.parse_knowledge_file(path, content)
            self.repository.upsert_item(item, resolved, content_hash, stat.st_mtime, stat.st_size)

        stale_paths = [path for path in indexed if path not in current_paths]
        stale_ids = self.repository.query_stale_ids(stale_paths)
        for knowledge_id in stale_ids:
            self.repository.delete_item(knowledge_id)

        self.repository.update_index_metadata("last_sync", str(len(files)))
        self.repository.commit()

        all_items = self.repository.all_items()
        self.embedding_model.fit(all_items)
        set_embedding_model(self.embedding_model)
        return len(files)

    def get_indexed_count(self) -> int:
        return len(self.repository.all_items())
