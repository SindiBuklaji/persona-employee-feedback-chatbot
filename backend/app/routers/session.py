from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.data.vignette import FOLLOW_UP_SEQUENCE, VIGNETTE_TEXT, VIGNETTE_TITLE, get_follow_up_prompt
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
        forced_condition = True
    else:
        condition = assign_condition()
        forced_condition = False

    now = datetime.utcnow()
    participant = Participant(
        consent_given=True,
        condition=condition,
        forced_condition=forced_condition,
        timestamp_session_start=now,
        completion_stage="vignette",
    )
    db.add(participant)
    db.commit()
    db.refresh(participant)

    opening_message = opening_message_for_condition(condition, get_follow_up_prompt(condition, FOLLOW_UP_SEQUENCE[0]["key"]))

    return StartSessionResponse(
        participant_id=participant.participant_id,
        condition=condition,
        vignette_title=VIGNETTE_TITLE,
        vignette_text=VIGNETTE_TEXT,
        opening_message=opening_message,
        min_turns=settings.min_turns,
        max_turns=settings.max_turns,
    )
