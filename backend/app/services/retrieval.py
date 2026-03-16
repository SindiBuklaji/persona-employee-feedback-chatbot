from __future__ import annotations

from dataclasses import dataclass

from openai import OpenAI

from app.config import settings
from app.data.retrieval_corpus import RETRIEVAL_DOCUMENTS


@dataclass
class RetrievedDoc:
    doc_id: str
    title: str
    text: str
    score: float


class RetrievalService:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.documents = RETRIEVAL_DOCUMENTS
        self._doc_embeddings: list[list[float]] | None = None

    def _embed(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model=settings.openai_embedding_model,
            input=text,
        )
        return response.data[0].embedding

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(y * y for y in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def _ensure_embeddings(self) -> None:
        if self._doc_embeddings is None:
            self._doc_embeddings = [self._embed(doc["text"]) for doc in self.documents]

    def retrieve(self, query: str, top_k: int | None = None) -> list[RetrievedDoc]:
        self._ensure_embeddings()
        query_embedding = self._embed(query)
        k = top_k or settings.top_k_retrieval

        scored = []
        for doc, emb in zip(self.documents, self._doc_embeddings or []):
            score = self._cosine_similarity(query_embedding, emb)
            scored.append(
                RetrievedDoc(
                    doc_id=doc["id"],
                    title=doc["title"],
                    text=doc["text"],
                    score=score,
                )
            )

        return sorted(scored, key=lambda x: x.score, reverse=True)[:k]
