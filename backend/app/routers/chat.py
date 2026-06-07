from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.data.vignette import FOLLOW_UP_SEQUENCE
from app.db import get_db
from app.models import Participant
from app.schemas import ChatMessageOut, ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])
chat_service = ChatService()


class FinishChatRequest(BaseModel):
    participant_id: str


class FinishChatResponse(BaseModel):
    participant_id: str
    chat_completed: bool


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    participant = db.get(Participant, payload.participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found.")
    if participant.chat_completed:
        raise HTTPException(status_code=400, detail="Chat already completed.")

    # Enforce hard cap on turns
    if participant.total_turns >= settings.max_turns:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum turns ({settings.max_turns}) reached. Please finish the chat."
        )

    # Set chat start timestamp on first turn
    if participant.total_turns == 0:
        participant.timestamp_chat_start = datetime.utcnow()
        participant.completion_stage = "chat"

    assistant_message = chat_service.process_user_message(db, participant, payload.message)

    turns_used = participant.total_turns

    # Task is complete when all follow-up questions have been asked
    # This is backend-driven, not LLM-driven
    task_complete = turns_used >= len(FOLLOW_UP_SEQUENCE)

    return ChatResponse(
        participant_id=participant.participant_id,
        condition=participant.condition,
        assistant_message=ChatMessageOut(
            role=assistant_message.role,
            content=assistant_message.content,
            turn_index=assistant_message.turn_index,
            follow_up_key=assistant_message.follow_up_key,
        ),
        turns_used=turns_used,
        chat_completed=task_complete,  # True when all follow-ups done, False otherwise
    )


@router.post("/finish", response_model=FinishChatResponse)
def finish_chat(payload: FinishChatRequest, db: Session = Depends(get_db)) -> FinishChatResponse:
    """Allow user to finish chat after minimum turns, proceed to questionnaire."""
    participant = db.get(Participant, payload.participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found.")
    if participant.chat_completed:
        raise HTTPException(status_code=400, detail="Chat already completed.")

    # Enforce minimum turns before allowing finish
    if participant.total_turns < settings.min_turns:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum {settings.min_turns} turns required before finishing. You have completed {participant.total_turns} turn(s)."
        )

    now = datetime.utcnow()
    participant.chat_completed = True
    participant.timestamp_chat_end = now
    participant.completion_stage = "questionnaire"
    db.commit()

    return FinishChatResponse(
        participant_id=participant.participant_id,
        chat_completed=True,
    )
