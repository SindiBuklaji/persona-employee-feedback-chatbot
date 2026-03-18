from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
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

    assistant_message = chat_service.process_user_message(db, participant, payload.message)

    turns_used = participant.total_turns

    return ChatResponse(
        participant_id=participant.id,
        condition=participant.condition,
        assistant_message=ChatMessageOut(
            role=assistant_message.role,
            content=assistant_message.content,
            turn_index=assistant_message.turn_index,
            follow_up_key=assistant_message.follow_up_key,
        ),
        turns_used=turns_used,
        chat_completed=participant.chat_completed,
    )


@router.post("/finish", response_model=FinishChatResponse)
def finish_chat(payload: FinishChatRequest, db: Session = Depends(get_db)) -> FinishChatResponse:
    """Allow user to finish chat at any point and proceed to questionnaire."""
    participant = db.get(Participant, payload.participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found.")
    if participant.chat_completed:
        raise HTTPException(status_code=400, detail="Chat already completed.")

    participant.chat_completed = True
    participant.finished_chat_at = datetime.utcnow()
    db.commit()

    return FinishChatResponse(
        participant_id=participant.id,
        chat_completed=True,
    )
