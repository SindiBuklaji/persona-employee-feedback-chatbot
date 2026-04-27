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
        select(Participant).where(Participant.participant_id == payload.participant_id)
    ).scalar_one_or_none()

    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found.")

    feedback_honesty_index = (
        payload.criticality + payload.specificity + payload.riskiness
    ) / 3.0

    coding = HonestyCodings(
        participant_id=payload.participant_id,
        coder_id=payload.coder_id,
        criticality=payload.criticality,
        specificity=payload.specificity,
        riskiness=payload.riskiness,
        feedback_honesty_index=feedback_honesty_index,
        timestamp_coded=datetime.utcnow(),
        coding_notes=payload.coding_notes,
    )
    db.add(coding)
    db.commit()
    db.refresh(coding)

    return HonestyCodeOut(
        coding_id=coding.coding_id,
        participant_id=coding.participant_id,
        coder_id=coding.coder_id,
        criticality=coding.criticality,
        specificity=coding.specificity,
        riskiness=coding.riskiness,
        feedback_honesty_index=coding.feedback_honesty_index,
        coding_notes=coding.coding_notes,
        timestamp_coded=coding.timestamp_coded.isoformat(),
    )


@router.get("/{participant_id}", response_model=list[HonestyCodeOut])
def list_honesty_codings(participant_id: str, db: Session = Depends(get_db)) -> list[HonestyCodeOut]:
    """List all codings for a participant."""
    participant = db.execute(
        select(Participant).where(Participant.participant_id == participant_id)
    ).scalar_one_or_none()

    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found.")

    codings = db.execute(
        select(HonestyCodings).where(HonestyCodings.participant_id == participant_id)
    ).scalars().all()

    return [
        HonestyCodeOut(
            coding_id=coding.coding_id,
            participant_id=coding.participant_id,
            coder_id=coding.coder_id,
            criticality=coding.criticality,
            specificity=coding.specificity,
            riskiness=coding.riskiness,
            feedback_honesty_index=coding.feedback_honesty_index,
            coding_notes=coding.coding_notes,
            timestamp_coded=coding.timestamp_coded.isoformat(),
        )
        for coding in codings
    ]
