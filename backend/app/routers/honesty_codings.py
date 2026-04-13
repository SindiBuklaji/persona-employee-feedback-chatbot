from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import HonestyCodings, Participant
from app.schemas import HonestyCodeOut, HonestyCodeRequest

router = APIRouter(prefix="/honesty-codings", tags=["honesty_codings"])


@router.post("", response_model=HonestyCodeOut)
def create_honesty_coding(payload: HonestyCodeRequest, db: Session = Depends(get_db)) -> HonestyCodeOut:
    """Submit a coding for a participant."""
    participant = db.execute(
        select(Participant).where(Participant.id == payload.participant_id)
    ).scalar_one_or_none()

    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found.")

    feedback_honesty_index = (
        payload.criticality_score + payload.specificity_score + payload.riskiness_score
    ) / 3.0

    coding = HonestyCodings(
        id=str(uuid4()),
        participant_id=payload.participant_id,
        coder_id=payload.coder_id,
        criticality_score=payload.criticality_score,
        specificity_score=payload.specificity_score,
        riskiness_score=payload.riskiness_score,
        feedback_honesty_index=feedback_honesty_index,
        coded_at=datetime.utcnow(),
        notes=payload.notes,
    )
    db.add(coding)
    db.commit()
    db.refresh(coding)

    return HonestyCodeOut(
        id=coding.id,
        participant_id=coding.participant_id,
        coder_id=coding.coder_id,
        criticality_score=coding.criticality_score,
        specificity_score=coding.specificity_score,
        riskiness_score=coding.riskiness_score,
        feedback_honesty_index=coding.feedback_honesty_index,
        coded_at=coding.coded_at.isoformat(),
        notes=coding.notes,
    )


@router.get("/{participant_id}")
def list_honesty_codings(participant_id: str, db: Session = Depends(get_db)):
    """List all codings for a participant."""
    participant = db.execute(
        select(Participant).where(Participant.id == participant_id)
    ).scalar_one_or_none()

    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found.")

    codings = db.execute(
        select(HonestyCodings).where(HonestyCodings.participant_id == participant_id)
    ).scalars().all()

    return [
        HonestyCodeOut(
            id=coding.id,
            participant_id=coding.participant_id,
            coder_id=coding.coder_id,
            criticality_score=coding.criticality_score,
            specificity_score=coding.specificity_score,
            riskiness_score=coding.riskiness_score,
            feedback_honesty_index=coding.feedback_honesty_index,
            coded_at=coding.coded_at.isoformat(),
            notes=coding.notes,
        )
        for coding in codings
    ]
