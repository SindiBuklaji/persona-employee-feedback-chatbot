import csv
import io

from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import HonestyCodings, Message, Participant, QuestionnaireResponse, RetrievalLog

router = APIRouter(prefix="/export", tags=["export"])


def verify_admin_token(authorization: str = Header(None)) -> None:
    """Verify the admin token from Authorization header.

    Expected format: "Bearer <token>"
    """
    if not settings.admin_token:
        # In development (no admin_token set), allow all exports
        return

    if not authorization:
        raise HTTPException(status_code=401, detail="Admin token required")

    try:
        scheme, token = authorization.split(" ", 1)
        if scheme.lower() != "bearer":
            raise ValueError("Invalid authorization scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

    if token != settings.admin_token:
        raise HTTPException(status_code=401, detail="Invalid admin token")

    return


@router.get("/transcripts.csv")
def export_transcripts(db: Session = Depends(get_db), _: None = Depends(verify_admin_token)) -> StreamingResponse:
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
        .join(Participant, Message.participant_id == Participant.participant_id)
        .order_by(Message.participant_id, Message.turn_index)
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
def export_participants(db: Session = Depends(get_db), _: None = Depends(verify_admin_token)) -> StreamingResponse:
    """Export engagement metrics and completion status for all participants."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([
        "participant_id",
        "condition",
        "completed_task",
        "number_user_turns",
        "total_user_word_count",
        "average_user_message_length",
        "started_at",
        "completed_at",
        "dropout_stage",
        "created_at",
    ])

    participants = db.execute(select(Participant)).scalars().all()
    for participant in participants:
        writer.writerow([
            participant.participant_id,
            participant.condition,
            participant.session_completed,
            participant.total_turns,
            participant.total_user_words,
            participant.average_user_message_length,
            participant.timestamp_session_start.isoformat() if participant.timestamp_session_start else None,
            participant.timestamp_questionnaire_submit.isoformat() if participant.timestamp_questionnaire_submit else None,
            participant.dropout_stage,
            participant.created_at.isoformat() if participant.created_at else None,
        ])

    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=participants.csv"},
    )


@router.get("/questionnaires.csv")
def export_questionnaires(db: Session = Depends(get_db), _: None = Depends(verify_admin_token)) -> StreamingResponse:
    """Export all questionnaire responses with perception, safety, and openness items."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([
        "participant_id",
        "condition",
        # Perception items - Warmth
        "perc_warm_friendly",
        "perc_warm_understanding",
        "perc_warm_comfortable",
        # Perception items - Structured/Direct
        "perc_struct_direct",
        "perc_struct_professional",
        "perc_struct_task_focused",
        "perceived_warmth_mean",
        "perceived_competence_mean",
        # Psychological safety items
        "psych_safe_1",
        "psych_safe_2",
        "psych_safe_3",
        "psych_safe_4",
        "psych_safe_5",
        "psychological_safety_mean",
        # Openness/honesty items
        "openness_1",
        "openness_2",
        "openness_3",
        "openness_4",
        "self_reported_honesty_mean",
        # Control variables
        "ai_experience",
        "years_work_experience",
        "age",
        "gender",
        "industry",
        "job_role",
        "timestamp_submit",
    ])

    stmt = (
        select(QuestionnaireResponse, Participant.condition)
        .join(Participant, QuestionnaireResponse.participant_id == Participant.participant_id)
    )

    for questionnaire, condition in db.execute(stmt).all():
        writer.writerow([
            questionnaire.participant_id,
            condition,
            # Perception items - Warmth
            questionnaire.perc_warm_friendly,
            questionnaire.perc_warm_understanding,
            questionnaire.perc_warm_comfortable,
            # Perception items - Structured/Direct
            questionnaire.perc_struct_direct,
            questionnaire.perc_struct_professional,
            questionnaire.perc_struct_task_focused,
            questionnaire.perceived_warmth_mean,
            questionnaire.perceived_competence_mean,
            # Psychological safety items
            questionnaire.psych_safe_1,
            questionnaire.psych_safe_2,
            questionnaire.psych_safe_3,
            questionnaire.psych_safe_4,
            questionnaire.psych_safe_5,
            questionnaire.psychological_safety_mean,
            # Openness/honesty items
            questionnaire.openness_1,
            questionnaire.openness_2,
            questionnaire.openness_3,
            questionnaire.openness_4,
            questionnaire.self_reported_honesty_mean,
            # Control variables
            questionnaire.ai_experience,
            questionnaire.years_work_experience,
            questionnaire.age,
            questionnaire.gender,
            questionnaire.industry,
            questionnaire.job_role,
            questionnaire.timestamp_submit.isoformat() if questionnaire.timestamp_submit else None,
        ])

    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=questionnaires.csv"},
    )


@router.get("/honesty_codings.csv")
def export_honesty_codings(db: Session = Depends(get_db), _: None = Depends(verify_admin_token)) -> StreamingResponse:
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
        .join(Participant, HonestyCodings.participant_id == Participant.participant_id)
        .order_by(HonestyCodings.participant_id, HonestyCodings.timestamp_coded)
    )

    for coding, condition in db.execute(stmt).all():
        writer.writerow([
            coding.coding_id,
            coding.participant_id,
            condition,
            coding.coder_id,
            coding.criticality,
            coding.specificity,
            coding.riskiness,
            coding.feedback_honesty_index,
            coding.timestamp_coded.isoformat(),
            coding.coding_notes,
        ])

    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=honesty_codings.csv"},
    )


@router.get("/retrieval_logs.csv")
def export_retrieval_logs(db: Session = Depends(get_db), _: None = Depends(verify_admin_token)) -> StreamingResponse:
    """Export retrieval logs for auditability and reproducibility.

    Note: User messages are stored in the messages table and linked via message_id.
    Retrieval logs contain only aggregate metadata needed for analysis.
    """
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([
        "participant_id",
        "condition",
        "turn_index",
        "message_id",
        "retrieved_card_ids",
        "retrieved_card_constructs",
        "retrieval_scores",
        "retrieval_method",
        "retrieval_enabled",
        "retrieval_top_k",
        "corpus_version",
        "timestamp_created",
    ])

    stmt = (
        select(RetrievalLog, Participant.condition)
        .join(Participant, RetrievalLog.participant_id == Participant.participant_id)
        .order_by(RetrievalLog.participant_id, RetrievalLog.turn_index)
    )

    for log, condition in db.execute(stmt).all():
        writer.writerow([
            log.participant_id,
            condition,
            log.turn_index,
            log.message_id,
            log.retrieved_card_ids,
            log.retrieved_card_constructs,
            log.retrieval_scores,
            log.retrieval_method,
            log.retrieval_enabled,
            log.retrieval_top_k,
            log.corpus_version,
            log.timestamp_created.isoformat(),
        ])

    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=retrieval_logs.csv"},
    )


@router.get("/analysis_dataset.csv")
def export_analysis_dataset(db: Session = Depends(get_db), _: None = Depends(verify_admin_token)) -> StreamingResponse:
    """Export combined analysis dataset: one row per participant with all engagement, perception, and outcome measures."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([
        # Participant & condition
        "participant_id",
        "condition",
        # Engagement metrics
        "completed_task",
        "number_user_turns",
        "total_user_word_count",
        "average_user_message_length",
        # Perception measures - Warmth
        "perc_warm_friendly",
        "perc_warm_understanding",
        "perc_warm_comfortable",
        "perceived_warmth_score",
        # Perception measures - Structured/Direct
        "perc_struct_direct",
        "perc_struct_professional",
        "perc_struct_task_focused",
        "perceived_competence_score",
        # Psychological safety measures
        "psych_safe_1",
        "psych_safe_2",
        "psych_safe_3",
        "psych_safe_4",
        "psych_safe_5",
        "psychological_safety_score",
        # Openness/honesty measures
        "openness_1",
        "openness_2",
        "openness_3",
        "openness_4",
        "self_reported_honesty_score",
        # Control variables
        "prior_ai_experience",
        "years_work_experience",
        "age",
        "gender",
        "industry",
        "job_role",
    ])

    participants = db.execute(select(Participant)).scalars().all()
    for participant in participants:
        # Get questionnaire if exists
        questionnaire = db.query(QuestionnaireResponse).filter(
            QuestionnaireResponse.participant_id == participant.participant_id
        ).first()

        writer.writerow([
            # Participant & condition
            participant.participant_id,
            participant.condition,
            # Engagement metrics
            int(participant.session_completed),
            participant.total_turns,
            participant.total_user_words,
            participant.average_user_message_length or "",
            # Perception measures - Warmth
            questionnaire.perc_warm_friendly if questionnaire else "",
            questionnaire.perc_warm_understanding if questionnaire else "",
            questionnaire.perc_warm_comfortable if questionnaire else "",
            questionnaire.perceived_warmth_mean if questionnaire else "",
            # Perception measures - Structured/Direct
            questionnaire.perc_struct_direct if questionnaire else "",
            questionnaire.perc_struct_professional if questionnaire else "",
            questionnaire.perc_struct_task_focused if questionnaire else "",
            questionnaire.perceived_competence_mean if questionnaire else "",
            # Psychological safety measures
            questionnaire.psych_safe_1 if questionnaire else "",
            questionnaire.psych_safe_2 if questionnaire else "",
            questionnaire.psych_safe_3 if questionnaire else "",
            questionnaire.psych_safe_4 if questionnaire else "",
            questionnaire.psych_safe_5 if questionnaire else "",
            questionnaire.psychological_safety_mean if questionnaire else "",
            # Openness/honesty measures
            questionnaire.openness_1 if questionnaire else "",
            questionnaire.openness_2 if questionnaire else "",
            questionnaire.openness_3 if questionnaire else "",
            questionnaire.openness_4 if questionnaire else "",
            questionnaire.self_reported_honesty_mean if questionnaire else "",
            # Control variables
            questionnaire.ai_experience if questionnaire else "",
            questionnaire.years_work_experience if questionnaire else "",
            questionnaire.age if questionnaire else "",
            questionnaire.gender if questionnaire else "",
            questionnaire.industry if questionnaire else "",
            questionnaire.job_role if questionnaire else "",
        ])

    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=analysis_dataset.csv"},
    )
