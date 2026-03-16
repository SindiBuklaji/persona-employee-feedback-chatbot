from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.data.vignette import FOLLOW_UP_SEQUENCE, VIGNETTE_TEXT, VIGNETTE_TITLE
from app.db import get_db
from app.models import Participant
from app.schemas import StartSessionRequest, StartSessionResponse
from app.services.personas import opening_message_for_condition
from app.services.randomization import assign_condition

router = APIRouter(prefix="/session", tags=["session"])


@router.post("/start", response_model=StartSessionResponse)
def start_session(payload: StartSessionRequest, db: Session = Depends(get_db)) -> StartSessionResponse:
    if not payload.consented:
        raise HTTPException(status_code=400, detail="Consent is required to continue.")

    if getattr(payload, "forced_condition", None) in {"warm", "competent"}:
        condition = payload.forced_condition
    else:
        condition = assign_condition()
    participant = Participant(
        consented=True,
        condition=condition,
        started_chat_at=datetime.utcnow(),
    )
    db.add(participant)
    db.commit()
    db.refresh(participant)

    opening_message = opening_message_for_condition(condition, FOLLOW_UP_SEQUENCE[0]["prompt"])

    return StartSessionResponse(
        participant_id=participant.id,
        condition=condition,
        vignette_title=VIGNETTE_TITLE,
        vignette_text=VIGNETTE_TEXT,
        opening_message=opening_message,
        max_turns=settings.max_turns,
    )
