"""
Debug endpoints for development and testing.

Only available when DEBUG=true environment variable is set.
Endpoints are conditionally registered in main.py.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.services.retrieval import RetrievalService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/debug", tags=["debug"])


class RetrievalDebugRequest(BaseModel):
    query: str


class RetrievalDebugResponse(BaseModel):
    query: str
    retrieved_count: int
    retrieval_method: str
    cards: list[dict]


@router.post("/retrieval", response_model=RetrievalDebugResponse)
def debug_retrieval(payload: RetrievalDebugRequest) -> RetrievalDebugResponse:
    """Test retrieval with a sample query.

    Only available in debug mode. Returns retrieved card details for inspection.
    """
    if not settings.debug:
        raise HTTPException(status_code=403, detail="Debug mode not enabled")

    retrieval = RetrievalService()
    retrieved_docs, retrieval_method = retrieval.retrieve(payload.query, top_k=settings.top_k_retrieval)

    cards = []
    for doc in retrieved_docs:
        cards.append({
            "id": doc.doc_id,
            "construct": doc.construct,
            "category": doc.category,
            "tags": doc.tags,
            "score": round(doc.score, 4),
            "evidence_summary": doc.text.split("\n\nGuidance:")[0][:200] + "...",
        })

    return RetrievalDebugResponse(
        query=payload.query,
        retrieved_count=len(retrieved_docs),
        retrieval_method=retrieval_method,
        cards=cards,
    )


@router.get("/retrieval")
def debug_retrieval_get(q: str = None) -> RetrievalDebugResponse:
    """Test retrieval with a query string parameter.

    Example: GET /debug/retrieval?q=I+do+not+feel+safe+giving+feedback
    """
    if not settings.debug:
        raise HTTPException(status_code=403, detail="Debug mode not enabled")

    if not q:
        raise HTTPException(status_code=400, detail="Query parameter 'q' required")

    retrieval = RetrievalService()
    retrieved_docs, retrieval_method = retrieval.retrieve(q, top_k=settings.top_k_retrieval)

    cards = []
    for doc in retrieved_docs:
        cards.append({
            "id": doc.doc_id,
            "construct": doc.construct,
            "category": doc.category,
            "tags": doc.tags,
            "score": round(doc.score, 4),
            "evidence_summary": doc.text.split("\n\nGuidance:")[0][:200] + "...",
        })

    return RetrievalDebugResponse(
        query=q,
        retrieved_count=len(retrieved_docs),
        retrieval_method=retrieval_method,
        cards=cards,
    )
