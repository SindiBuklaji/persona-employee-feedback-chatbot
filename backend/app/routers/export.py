import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import HonestyCodings, Message, Participant, QuestionnaireResponse

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


@router.get("/participants.csv")
def export_participants(db: Session = Depends(get_db)) -> StreamingResponse:
    """Export all participants with aggregate session data."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([
        "participant_id",
        "condition",
        "consented",
        "started_at",
        "finished_chat_at",
        "task_completed",
        "turn_count",
        "total_user_word_count",
        "dropout_stage",
        "forced_condition_used",
        "created_at",
    ])

    participants = db.execute(select(Participant)).scalars().all()
    for participant in participants:
        writer.writerow([
            participant.id,
            participant.condition,
            participant.consented,
            participant.started_chat_at.isoformat() if participant.started_chat_at else None,
            participant.finished_chat_at.isoformat() if participant.finished_chat_at else None,
            participant.session_completed,
            participant.total_turns,
            participant.total_user_words,
            participant.dropout_stage,
            participant.forced_condition_used,
            participant.created_at.isoformat(),
        ])

    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=participants.csv"},
    )


@router.get("/questionnaires.csv")
def export_questionnaires(db: Session = Depends(get_db)) -> StreamingResponse:
    """Export all questionnaire responses."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([
        "participant_id",
        "condition",
        "manip_warmth_friendly",
        "manip_warmth_sincere",
        "manip_competence_competent",
        "manip_competence_skilled",
        "psych_safe_1",
        "psych_safe_2",
        "psych_safe_3",
        "psych_safe_4",
        "psych_safe_5",
        "psych_safety_mean",
        "ai_experience",
        "organizational_tenure_years",
        "age",
        "gender",
        "industry",
        "job_role",
        "created_at",
    ])

    stmt = (
        select(QuestionnaireResponse, Participant.condition)
        .join(Participant, QuestionnaireResponse.participant_id == Participant.id)
    )

    for questionnaire, condition in db.execute(stmt).all():
        writer.writerow([
            questionnaire.participant_id,
            condition,
            questionnaire.manip_warmth_friendly,
            questionnaire.manip_warmth_sincere,
            questionnaire.manip_competence_competent,
            questionnaire.manip_competence_skilled,
            questionnaire.psych_safe_1,
            questionnaire.psych_safe_2,
            questionnaire.psych_safe_3,
            questionnaire.psych_safe_4,
            questionnaire.psych_safe_5,
            questionnaire.psych_safety_mean,
            questionnaire.ai_experience,
            questionnaire.organizational_tenure_years,
            questionnaire.age,
            questionnaire.gender,
            questionnaire.industry,
            questionnaire.job_role,
            questionnaire.created_at.isoformat(),
        ])

    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=questionnaires.csv"},
    )


@router.get("/honesty_codings.csv")
def export_honesty_codings(db: Session = Depends(get_db)) -> StreamingResponse:
    """Export all honesty codings."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([
        "coding_id",
        "participant_id",
        "condition",
        "coder_id",
        "criticality_score",
        "specificity_score",
        "riskiness_score",
        "feedback_honesty_index",
        "coded_at",
        "notes",
    ])

    stmt = (
        select(HonestyCodings, Participant.condition)
        .join(Participant, HonestyCodings.participant_id == Participant.id)
        .order_by(HonestyCodings.participant_id, HonestyCodings.coded_at)
    )

    for coding, condition in db.execute(stmt).all():
        writer.writerow([
            coding.id,
            coding.participant_id,
            condition,
            coding.coder_id,
            coding.criticality_score,
            coding.specificity_score,
            coding.riskiness_score,
            coding.feedback_honesty_index,
            coding.coded_at.isoformat(),
            coding.notes,
        ])

    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=honesty_codings.csv"},
    )
