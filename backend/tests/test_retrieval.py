"""
Retrieval corpus validation and smoke tests.

Run with: cd backend && python tests/test_retrieval.py
Or: cd backend && python -m pytest tests/test_retrieval.py -v
"""

import json
import logging
import sys
from pathlib import Path

# Add parent directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent))

# Test corpus loading
def test_corpus_load():
    """Validate corpus JSON and structure."""
    corpus_path = Path(__file__).parent.parent / "app" / "data" / "retrieval_corpus.json"
    assert corpus_path.exists(), f"Corpus file not found at {corpus_path}"

    with open(corpus_path) as f:
        corpus = json.load(f)

    # Check metadata
    assert "corpus_metadata" in corpus
    metadata = corpus["corpus_metadata"]
    assert metadata.get("total_cards") == 25, f"Expected 25 cards, got {metadata.get('total_cards')}"

    # Check evidence items
    assert "evidence_items" in corpus
    items = corpus["evidence_items"]
    assert len(items) == 25, f"Expected 25 items, got {len(items)}"

    # Validate each item
    required_fields = {
        "id", "construct", "complete_citation", "source_type", "category",
        "tags", "evidence_summary", "chatbot_behavior_guidance",
        "why_useful_for_participant_conversations", "participant_visible", "verification"
    }

    for i, item in enumerate(items):
        missing = required_fields - set(item.keys())
        assert not missing, f"Item {i} ({item.get('id')}) missing fields: {missing}"
        assert item.get("participant_visible") is False, f"Item {item['id']} participant_visible != false"

        verification = item.get("verification", {})
        assert verification.get("metadata_verified"), f"Item {item['id']} metadata not verified"
        assert verification.get("content_relevance_verified"), f"Item {item['id']} content not verified"
        assert verification.get("included_in_final_corpus"), f"Item {item['id']} not included"

    print(f"[OK] Corpus validation passed: {len(items)} cards, all fields present and verified")


def test_retrieval_service():
    """Test retrieval service with sample queries and expected category matching."""
    from app.services.retrieval import RetrievalService

    service = RetrievalService()

    # Test queries with expected category matching rules
    test_queries = {
        "safety": {
            "query": "I do not feel safe giving honest feedback to my manager.",
            "expected_categories": ["1_psychological_safety_and_speaking_up", "2_employee_voice_and_organizational_silence"],
            "min_match": 2,  # At least 2 of top 3 from these categories
        },
        "workload": {
            "query": "My workload is too much and priorities keep changing.",
            "expected_categories": ["5_workload_stress_and_role_ambiguity"],
            "min_match": 2,  # At least 2 of top 3 from this category
        },
        "recognition": {
            "query": "I feel like my work is not recognized.",
            "expected_categories": ["6_recognition_fairness_and_belonging"],
            "min_match": 2,  # At least 2 of top 3 from this category
        },
        "conflict": {
            "query": "I had a conflict with a colleague and now I avoid speaking up.",
            "expected_categories": ["7_workplace_conflict_and_negative_experiences"],
            "min_match": 1,  # At least 1 of top 3 from this category
        },
        "confidentiality": {
            "query": "I am not sure whether my feedback will stay confidential.",
            "expected_categories": ["8_confidentiality_and_trust_in_feedback_settings"],
            "min_match": 1,  # At least 1 of top 2 from this category
        },
    }

    print("\n" + "=" * 70)
    print("RETRIEVAL SERVICE SMOKE TEST WITH CATEGORY VALIDATION")
    print("=" * 70)

    all_passed = True

    for test_name, test_config in test_queries.items():
        query = test_config["query"]
        expected_cats = test_config["expected_categories"]
        min_match = test_config["min_match"]

        retrieved, method = service.retrieve(query, top_k=3)

        print(f"\n[{test_name.upper()}]")
        print(f"Query: {query}")
        print(f"Method: {method}")
        print(f"Cards retrieved: {len(retrieved)}")

        for i, doc in enumerate(retrieved, 1):
            print(f"  {i}. {doc.doc_id} ({doc.construct})")
            print(f"     Category: {doc.category}")
            print(f"     Tags: {', '.join(doc.tags[:3])}...")
            print(f"     Score: {doc.score:.4f}")

        # Check category matching
        categories = [doc.category for doc in retrieved]
        matching_count = sum(1 for cat in categories if cat in expected_cats)
        print(f"  Expected categories: {expected_cats}")
        print(f"  Matched: {matching_count}/{min_match} required")

        # Validate
        test_passed = matching_count >= min_match
        status = "[PASS]" if test_passed else "[FAIL]"
        print(f"  {status} {matching_count}/{min_match} cards from expected categories")

        if not test_passed:
            all_passed = False

        assert len(retrieved) > 0, f"No cards retrieved for {test_name}"
        assert len(retrieved) <= 3, f"Too many cards retrieved for {test_name}"
        assert test_passed, f"{test_name} test failed: got {matching_count}, expected {min_match}"

    print("\n" + "=" * 70)
    if all_passed:
        print("[OK] All category validation tests passed")
    else:
        print("[FAIL] Some category validation tests failed")
    print("=" * 70)


def test_corpus_legacy_format():
    """Test conversion to legacy format for retrieval service."""
    from app.data.retrieval_corpus import RETRIEVAL_DOCUMENTS, _EVIDENCE_ITEMS

    assert len(RETRIEVAL_DOCUMENTS) == 25, f"Expected 25 documents, got {len(RETRIEVAL_DOCUMENTS)}"

    for i, doc in enumerate(RETRIEVAL_DOCUMENTS):
        assert "id" in doc
        assert "title" in doc
        assert "text" in doc
        assert "construct" in doc
        assert "category" in doc
        assert "tags" in doc

    print(f"[OK] Legacy format test passed: {len(RETRIEVAL_DOCUMENTS)} documents ready")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("Testing retrieval corpus implementation...\n")

    test_corpus_load()
    test_corpus_legacy_format()
    test_retrieval_service()

    print("\n[SUCCESS] All tests passed!")
