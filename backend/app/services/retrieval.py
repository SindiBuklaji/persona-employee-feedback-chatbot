"""
Retrieval service for fixed evidence corpus.

Supports both semantic (embedding-based) and keyword-based fallback retrieval.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from openai import OpenAI

from app.config import settings
from app.data.retrieval_corpus import RETRIEVAL_DOCUMENTS

logger = logging.getLogger(__name__)


@dataclass
class RetrievedDoc:
    doc_id: str
    title: str
    text: str
    score: float
    construct: str | None = None
    category: str | None = None
    tags: list[str] | None = None


class RetrievalService:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.documents = RETRIEVAL_DOCUMENTS
        self._doc_embeddings: list[list[float]] | None = None
        self.use_embeddings = settings.retrieval_use_embeddings
        self.enabled = settings.retrieval_enabled

    def _embed(self, text: str) -> list[float]:
        """Create embedding for text using OpenAI API."""
        try:
            response = self.client.embeddings.create(
                model=settings.openai_embedding_model,
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Embedding failed: {e}. Falling back to keyword search.")
            return []

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two embedding vectors."""
        if not a or not b:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(y * y for y in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def _keyword_score(self, query: str, doc: dict) -> float:
        """Compute keyword overlap score between query and document."""
        query_words = set(query.lower().split())
        doc_text = (doc.get("title", "") + " " + doc.get("text", "")).lower()
        doc_words = set(doc_text.split())

        intersection = query_words & doc_words
        if not query_words:
            return 0.0
        return len(intersection) / len(query_words)

    def _tag_score(self, query: str, doc: dict) -> float:
        """Compute relevance score based on tag matches."""
        tags = doc.get("tags", [])
        query_lower = query.lower()

        matches = sum(1 for tag in tags if tag.lower() in query_lower or query_lower in tag.lower())
        if not tags:
            return 0.0
        return matches / len(tags)

    def _ensure_embeddings(self) -> None:
        """Lazily compute and cache embeddings for all documents."""
        if self._doc_embeddings is None and self.use_embeddings:
            try:
                self._doc_embeddings = [self._embed(doc["text"]) for doc in self.documents]
                logger.info(f"Computed embeddings for {len(self.documents)} documents")
            except Exception as e:
                logger.error(f"Failed to compute embeddings: {e}")
                self._doc_embeddings = []

    def retrieve(self, query: str, top_k: int | None = None) -> tuple[list[RetrievedDoc], str]:
        """Retrieve top K most relevant documents.

        Args:
            query: User query/message text
            top_k: Number of documents to retrieve

        Returns:
            Tuple of (list of RetrievedDoc, retrieval_method)
            retrieval_method is "embedding", "keyword_fallback", or "disabled"
        """
        if not self.enabled or not self.documents:
            return [], "disabled"

        k = top_k or settings.top_k_retrieval

        # Try embedding-based retrieval if enabled
        if self.use_embeddings:
            self._ensure_embeddings()
            if self._doc_embeddings and all(emb for emb in self._doc_embeddings):
                return self._retrieve_embedding(query, k), "embedding"

        # Fall back to keyword-based retrieval
        return self._retrieve_keyword(query, k), "keyword_fallback"

    def _retrieve_embedding(self, query: str, top_k: int) -> list[RetrievedDoc]:
        """Retrieve using semantic similarity with embeddings."""
        try:
            query_embedding = self._embed(query)
            if not query_embedding:
                return self._retrieve_keyword(query, top_k)

            scored = []
            for doc, emb in zip(self.documents, self._doc_embeddings or []):
                if not emb:
                    continue
                score = self._cosine_similarity(query_embedding, emb)
                scored.append(
                    RetrievedDoc(
                        doc_id=doc["id"],
                        title=doc["title"],
                        text=doc["text"],
                        score=score,
                        construct=doc.get("construct"),
                        category=doc.get("category"),
                        tags=doc.get("tags", []),
                    )
                )

            return sorted(scored, key=lambda x: x.score, reverse=True)[:top_k]
        except Exception as e:
            logger.error(f"Embedding retrieval failed: {e}")
            return self._retrieve_keyword(query, top_k)

    def _retrieve_keyword(self, query: str, top_k: int) -> list[RetrievedDoc]:
        """Retrieve using keyword and tag matching."""
        scored = []
        for doc in self.documents:
            keyword_score = self._keyword_score(query, doc)
            tag_score = self._tag_score(query, doc)
            combined_score = 0.7 * keyword_score + 0.3 * tag_score

            scored.append(
                RetrievedDoc(
                    doc_id=doc["id"],
                    title=doc["title"],
                    text=doc["text"],
                    score=combined_score,
                    construct=doc.get("construct"),
                    category=doc.get("category"),
                    tags=doc.get("tags", []),
                )
            )

        return sorted(scored, key=lambda x: x.score, reverse=True)[:top_k]
