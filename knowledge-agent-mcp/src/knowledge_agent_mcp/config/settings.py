from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class ServerSettings(BaseModel):
    transport: str = "stdio"
    name: str = "knowledge-agent-mcp"
    version: str = "0.1.0"


class RetrievalWeights(BaseModel):
    keyword: float = 0.30
    vector: float = 0.30
    category: float = 0.15
    domain: float = 0.10
    version: float = 0.08
    status_confidence: float = 0.05
    freshness: float = 0.02


class RetrievalSettings(BaseModel):
    default_top_k: int = 10
    max_top_k: int = 30
    max_context_tokens: int = 12000
    ranking_weights: RetrievalWeights = Field(default_factory=RetrievalWeights)


class AgentSettings(BaseModel):
    max_search_rounds: int = 4
    max_queries_per_round: int = 6
    max_results_per_query: int = 10
    max_items_to_read: int = 15
    max_output_tokens: int = 5000


class LLMSettings(BaseModel):
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"
    temperature: float = 0.1
    timeout_seconds: int = 60
    max_retries: int = 2


class EmbeddingSettings(BaseModel):
    provider: str = "local"
    model: str = "deterministic-token-vector"
    dimension: int = 0
    batch_size: int = 32


class Settings(BaseModel):
    knowledge_base_path: str = "./knowledge_base"
    database_path: str = "./data/knowledge.db"
    vector_index_path: str = "./data/vector_index"
    read_only: bool = True
    server: ServerSettings = Field(default_factory=ServerSettings)
    retrieval: RetrievalSettings = Field(default_factory=RetrievalSettings)
    agent: AgentSettings = Field(default_factory=AgentSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)

    @classmethod
    def load(cls, root: Path) -> "Settings":
        config_path = root / "config" / "settings.yaml"
        data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        return cls.model_validate(data)
