"""
Retrieval service for fixed evidence corpus.

Supports both semantic (embedding-based) and keyword-based fallback retrieval.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from openai import OpenAI

from app.config import settings
from app.data.retrieval_corpus import RETRIEVAL_DOCUMENTS

logger = logging.getLogger(__name__)

# Stopwords to exclude from keyword matching
STOPWORDS = {
    "i", "am", "is", "are", "the", "a", "an", "not", "my", "your", "our",
    "work", "feel", "like", "feedback", "manager", "team", "people", "thing",
    "things", "don't", "won't", "can't", "it", "that", "this", "or", "and",
    "to", "in", "on", "at", "be", "have", "do", "get", "make", "go", "know",
    "think", "about", "would", "could", "should", "if", "whether", "what",
    "which", "who", "when", "where", "how", "why"
}

# High-value phrase mappings for boosting
PHRASE_BOOSTS = {
    "recognition": {
        "phrases": [
            "not recognized", "not appreciated", "unappreciated", "overlooked",
            "undervalued", "not valued", "no recognition", "invisible", "ignored"
        ],
        "categories": ["6_recognition_fairness_and_belonging"],
        "boost": 2.0
    },
    "confidentiality": {
        "phrases": [
            "stay confidential", "keep confidential", "confidential", "privacy",
            "shared with others", "used against me", "private", "secret", "trust"
        ],
        "categories": ["8_confidentiality_and_trust_in_feedback_settings"],
        "boost": 2.0
    },
    "workload": {
        "phrases": [
            "too much", "overload", "overloaded", "priorities keep changing",
            "unclear priorities", "changing priorities", "workload", "overwhelm"
        ],
        "categories": ["5_workload_stress_and_role_ambiguity"],
        "boost": 2.0
    },
    "conflict": {
        "phrases": [
            "conflict", "colleague", "avoid meetings", "relationship tension",
            "relationship conflict", "tension", "disagreement", "argument"
        ],
        "categories": ["7_workplace_conflict_and_negative_experiences"],
        "boost": 2.0
    },
    "safety": {
        "phrases": [
            "not safe", "safe to speak", "afraid", "scared", "embarrass",
            "punish", "retaliation", "psychological safety"
        ],
        "categories": ["1_psychological_safety_and_speaking_up", "2_employee_voice_and_organizational_silence"],
        "boost": 2.0
    }
}

# Synonym mapping for keyword expansion
SYNONYMS = {
    "recognized": ["recognition", "valued", "appreciated", "acknowledged"],
    "appreciate": ["recognition", "valued", "valued"],
    "confidential": ["confidentiality", "privacy", "trust"],
    "workload": ["job_demands", "overload", "stress", "burnout"],
    "conflict": ["relationship_conflict", "task_conflict", "incivility"],
    "unclear": ["ambiguity", "clarity", "role_clarity"],
    "unheard": ["voice", "speaking_up"],
    "silence": ["organizational_silence", "voice_suppression"],
}


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
        """Compute keyword overlap score with stopword removal and phrase boosting."""
        # Clean and normalize query
        query_lower = query.lower()
        query_words = set(w for w in re.findall(r'\b\w+\b', query_lower) if w not in STOPWORDS)

        # Check for phrase boosts
        phrase_boost = 1.0
        for boost_key, boost_config in PHRASE_BOOSTS.items():
            for phrase in boost_config["phrases"]:
                if phrase in query_lower:
                    doc_category = doc.get("category", "")
                    if doc_category in boost_config["categories"]:
                        phrase_boost = max(phrase_boost, boost_config["boost"])
                        logger.debug(f"Phrase boost: '{phrase}' matched for {doc.get('id')}")

        # Get document text and extract meaningful words
        doc_text = (doc.get("title", "") + " " + doc.get("text", "")).lower()
        doc_words = set(w for w in re.findall(r'\b\w+\b', doc_text) if w not in STOPWORDS)

        # Compute base keyword overlap
        intersection = query_words & doc_words
        if not query_words:
            return 0.0
        base_score = len(intersection) / len(query_words)

        return base_score * phrase_boost

    def _tag_score(self, query: str, doc: dict) -> float:
        """Compute relevance score based on tag and category matches (heavily weighted)."""
        tags = doc.get("tags", [])
        category = doc.get("category", "")
        query_lower = query.lower()

        # Extract meaningful query words for matching
        query_words = set(w for w in re.findall(r'\b\w+\b', query_lower) if w not in STOPWORDS)

        # Check tag matches (exact and partial)
        tag_matches = 0
        for tag in tags:
            tag_lower = tag.lower()
            if tag_lower in query_lower or query_lower in tag_lower:
                tag_matches += 1
            # Check if any query word matches the tag
            if any(word in tag_lower for word in query_words):
                tag_matches += 0.5

        # Check category keyword matches (boost heavily)
        category_score = 0.0
        if "recognition" in query_lower and "6_recognition" in category:
            category_score = 2.0
        elif "confidential" in query_lower and "8_confidentiality" in category:
            category_score = 2.0
        elif ("workload" in query_lower or "priorities" in query_lower) and "5_workload" in category:
            category_score = 2.0
        elif "conflict" in query_lower and "7_workplace_conflict" in category:
            category_score = 2.0
        elif ("safe" in query_lower or "voice" in query_lower) and ("1_psychological" in category or "2_employee" in category):
            category_score = 1.5

        # Combine tag and category scores
        if not tags:
            return category_score if category_score > 0 else 0.0
        tag_score = min(tag_matches / len(tags), 1.0)
        return (tag_score + category_score) / 2 if category_score > 0 else tag_score

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
        """Retrieve using semantic similarity with embeddings, boosted by category/phrase matching."""
        try:
            query_embedding = self._embed(query)
            if not query_embedding:
                return self._retrieve_keyword(query, top_k)

            query_lower = query.lower()
            scored = []

            for doc, emb in zip(self.documents, self._doc_embeddings or []):
                if not emb:
                    continue

                # Get base embedding similarity score
                embedding_score = self._cosine_similarity(query_embedding, emb)

                # Apply category boosts (same as keyword fallback)
                category_boost = 1.0
                doc_category = doc.get("category", "")

                if "recognition" in query_lower and "6_recognition" in doc_category:
                    category_boost = 1.5
                elif "confidential" in query_lower and "8_confidentiality" in doc_category:
                    category_boost = 1.5
                elif ("workload" in query_lower or "priorities" in query_lower) and "5_workload" in doc_category:
                    category_boost = 1.5
                elif "conflict" in query_lower and "7_workplace_conflict" in doc_category:
                    category_boost = 1.5
                elif ("safe" in query_lower or "voice" in query_lower) and ("1_psychological" in doc_category or "2_employee" in doc_category):
                    category_boost = 1.2

                # Apply phrase boosts (same as keyword fallback)
                for boost_key, boost_config in PHRASE_BOOSTS.items():
                    for phrase in boost_config["phrases"]:
                        if phrase in query_lower and doc_category in boost_config["categories"]:
                            category_boost = max(category_boost, 1.3)

                # Combine embedding score with category boost
                final_score = embedding_score * category_boost

                scored.append(
                    RetrievedDoc(
                        doc_id=doc["id"],
                        title=doc["title"],
                        text=doc["text"],
                        score=final_score,
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
        """Retrieve using keyword and tag matching with improved scoring."""
        scored = []
        for doc in self.documents:
            keyword_score = self._keyword_score(query, doc)
            tag_score = self._tag_score(query, doc)
            # Weight: 50% tag/category matching (most important), 50% keyword matching
            combined_score = 0.5 * tag_score + 0.5 * keyword_score

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

        results = sorted(scored, key=lambda x: x.score, reverse=True)[:top_k]
        if settings.debug:
            logger.info(f"Keyword retrieval for query '{query[:50]}...': returned {len(results)} cards with scores {[f'{r.score:.3f}' for r in results]}")
        return results
