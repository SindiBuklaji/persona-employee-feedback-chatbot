"""
Load fixed retrieval corpus from JSON file.

The corpus is a curated set of 25 evidence cards from peer-reviewed literature.
Each card provides background evidence to guide chatbot responses during
participant feedback conversations.

IMPORTANT: The corpus is hidden background knowledge. Do not expose evidence
cards, citations, or source information to participants.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

CORPUS_FILE_PATH = Path(__file__).parent / "retrieval_corpus.json"


def load_corpus() -> dict:
    """Load the fixed retrieval corpus from JSON file."""
    if not CORPUS_FILE_PATH.exists():
        raise FileNotFoundError(f"Retrieval corpus not found at {CORPUS_FILE_PATH}")

    with open(CORPUS_FILE_PATH, 'r', encoding='utf-8') as f:
        corpus = json.load(f)

    _validate_corpus(corpus)
    logger.info(f"Loaded retrieval corpus with {len(corpus.get('evidence_items', []))} cards")
    return corpus


def _validate_corpus(corpus: dict) -> None:
    """Validate corpus structure and content."""
    if not isinstance(corpus, dict):
        raise ValueError("Corpus must be a dict")

    metadata = corpus.get("corpus_metadata")
    if not metadata or metadata.get("total_cards") != 25:
        raise ValueError(f"Expected 25 cards, got {metadata.get('total_cards') if metadata else 0}")

    items = corpus.get("evidence_items", [])
    if len(items) != 25:
        raise ValueError(f"Expected 25 evidence items, got {len(items)}")

    required_fields = {
        "id", "construct", "complete_citation", "source_type", "category",
        "tags", "evidence_summary", "chatbot_behavior_guidance",
        "why_useful_for_participant_conversations", "participant_visible", "verification"
    }

    for i, item in enumerate(items):
        missing = required_fields - set(item.keys())
        if missing:
            raise ValueError(f"Evidence item {i} ({item.get('id')}) missing fields: {missing}")
        if item.get("participant_visible") is not False:
            raise ValueError(f"Evidence item {item.get('id')} has participant_visible != false")


def get_evidence_items() -> list[dict]:
    """Get list of evidence items from corpus."""
    corpus = load_corpus()
    return corpus.get("evidence_items", [])


try:
    _EVIDENCE_ITEMS = get_evidence_items()
    RETRIEVAL_DOCUMENTS = [
        {
            "id": item["id"],
            "title": item["construct"],
            "text": f"{item['evidence_summary']}\n\nGuidance: {item['chatbot_behavior_guidance']}",
            "construct": item["construct"],
            "category": item["category"],
            "tags": item.get("tags", []),
        }
        for item in _EVIDENCE_ITEMS
    ]
    CORPUS_LOADED = True
    logger.info(f"Retrieval corpus loaded: {len(RETRIEVAL_DOCUMENTS)} documents ready")
except Exception as e:
    logger.error(f"Failed to load retrieval corpus: {e}")
    CORPUS_LOADED = False
    RETRIEVAL_DOCUMENTS = []
    _EVIDENCE_ITEMS = []
