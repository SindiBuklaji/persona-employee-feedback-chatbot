import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Message, Participant

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/transcripts.csv")
def export_transcripts(db: Session = Depends(get_db)) -> StreamingResponse:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([
        "participant_id",
        "condition",
        "role",
        "content",
        "turn_index",
        "word_count",
        "created_at",
    ])

    stmt = (
        select(Message, Participant.condition)
        .join(Participant, Message.participant_id == Participant.id)
        .order_by(Message.participant_id, Message.turn_index, Message.created_at)
    )

    for message, condition in db.execute(stmt).all():
        writer.writerow([
            message.participant_id,
            condition,
            message.role,
            message.content,
            message.turn_index,
            message.word_count,
            message.created_at.isoformat(),
        ])

    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transcripts.csv"},
    )
