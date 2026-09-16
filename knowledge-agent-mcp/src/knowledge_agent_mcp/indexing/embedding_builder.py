from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any

from knowledge_agent_mcp.models.knowledge_item import KnowledgeItem


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9_\-\u4e00-\u9fff]+", text.lower())


class TfidfEmbedding:
    def __init__(self) -> None:
        self.vocabulary: dict[str, int] = {}
        self.idf: dict[str, float] = {}
        self._fitted = False

    def fit(self, items: list[KnowledgeItem]) -> None:
        doc_count = len(items)
        if doc_count == 0:
            return
        df: Counter[str] = Counter()
        doc_vectors: list[Counter[str]] = []
        for item in items:
            tokens = _tokenize(" ".join([item.title, item.summary or "", item.content[:2000]]))
            doc_vectors.append(Counter(tokens))
            df.update(set(tokens))
        self.vocabulary = {term: idx for idx, (term, _) in enumerate(df.most_common())}
        self.idf = {term: math.log((doc_count + 1) / (freq + 1)) + 1 for term, freq in df.items()}
        self._fitted = True

    def embed(self, text: str) -> list[float]:
        if not self._fitted or not self.vocabulary:
            return []
        tokens = _tokenize(text)
        tf = Counter(tokens)
        dim = len(self.vocabulary)
        vector = [0.0] * dim
        for term, count in tf.items():
            idx = self.vocabulary.get(term)
            if idx is not None:
                vector[idx] = count * self.idf.get(term, 1.0)
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]
        return vector

    def cosine_similarity(self, vec_a: list[float], vec_b: list[float]) -> float:
        if not vec_a or not vec_b:
            return 0.0
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(v * v for v in vec_a))
        norm_b = math.sqrt(sum(v * v for v in vec_b))
        if not norm_a or not norm_b:
            return 0.0
        return dot / (norm_a * norm_b)

    def fitted(self) -> bool:
        return self._fitted


def build_embedding_payload(text: str) -> dict[str, int]:
    return {"length": len(text)}


_GLOBAL_MODEL = TfidfEmbedding()


def get_embedding_model() -> TfidfEmbedding:
    return _GLOBAL_MODEL


def set_embedding_model(model: TfidfEmbedding) -> None:
    global _GLOBAL_MODEL
    _GLOBAL_MODEL = model
