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
    """Export all chat transcripts with proper error handling."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, quoting=csv.QUOTE_ALL)
    writer.writerow([
        "participant_id",
        "condition",
        "role",
        "content",
        "turn_index",
        "word_count",
        "created_at",
    ])

    try:
        stmt = (
            select(Message, Participant.condition)
            .join(Participant, Message.participant_id == Participant.participant_id)
            .order_by(Message.participant_id, Message.turn_index)
        )

        messages = db.execute(stmt).all()

        for message, condition in messages:
            writer.writerow([
                message.participant_id or "",
                condition or "",
                message.role or "",
                (message.content or "").replace('\n', ' ').replace('\r', ''),  # Clean newlines
                message.turn_index or 0,
                message.word_count or 0,
                message.timestamp_created.isoformat() if message.timestamp_created else "",
            ])

        buffer.seek(0)
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=transcripts.csv"},
        )
    except Exception as e:
        # Return error as CSV for debugging
        buffer = io.StringIO()
        buffer.write(f"Error exporting transcripts: {str(e)}\n")
        buffer.seek(0)
        raise HTTPException(status_code=500, detail=f"Error exporting transcripts: {str(e)}")


@router.get("/participants.csv")
def export_participants(db: Session = Depends(get_db), _: None = Depends(verify_admin_token)) -> StreamingResponse:
    """Export engagement metrics and completion status for all participants."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, quoting=csv.QUOTE_ALL)
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

    try:
        participants = db.execute(select(Participant)).scalars().all()
        for participant in participants:
            writer.writerow([
                participant.participant_id or "",
                participant.condition or "",
                participant.session_completed or "",
                participant.total_turns or "",
                participant.total_user_words or "",
                participant.average_user_message_length or "",
                participant.timestamp_session_start.isoformat() if participant.timestamp_session_start else "",
                participant.timestamp_questionnaire_submit.isoformat() if participant.timestamp_questionnaire_submit else "",
                participant.dropout_stage or "",
                participant.created_at.isoformat() if participant.created_at else "",
            ])

        buffer.seek(0)
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=participants.csv"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting participants: {str(e)}")


@router.get("/questionnaires.csv")
def export_questionnaires(db: Session = Depends(get_db), _: None = Depends(verify_admin_token)) -> StreamingResponse:
    """Export all questionnaire responses with manipulation check, safety, openness, and engagement items."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, quoting=csv.QUOTE_ALL)
    writer.writerow([
        "participant_id",
        "condition",
        # Manipulation check (bipolar items)
        "perc_warmth_bipolar",
        "perc_task_focus_bipolar",
        # Psychological safety items
        "psych_safe_1",
        "psych_safe_2",
        "psych_safe_3",
        "psychological_safety_mean",
        # Openness/honesty items
        "openness_1",
        "openness_2_reverse_coded",
        "self_reported_honesty_mean",
        # Engagement item
        "engagement_self_report",
        # Control variables
        "ai_experience",
        "years_work_experience",
        "age",
        "gender",
        "industry",
        "job_role",
        "timestamp_submit",
    ])

    try:
        stmt = (
            select(QuestionnaireResponse, Participant.condition)
            .join(Participant, QuestionnaireResponse.participant_id == Participant.participant_id)
        )

        for questionnaire, condition in db.execute(stmt).all():
            writer.writerow([
                questionnaire.participant_id or "",
                condition or "",
                # Manipulation check (bipolar items)
                questionnaire.perc_warmth_bipolar or "",
                questionnaire.perc_task_focus_bipolar or "",
                # Psychological safety items
                questionnaire.psych_safe_1 or "",
                questionnaire.psych_safe_2 or "",
                questionnaire.psych_safe_3 or "",
                questionnaire.psychological_safety_mean or "",
                # Openness/honesty items
                questionnaire.openness_1 or "",
                questionnaire.openness_2 or "",  # Raw value; reverse-code during analysis
                questionnaire.self_reported_honesty_mean or "",
                # Engagement item
                questionnaire.engagement_self_report or "",
                # Control variables
                questionnaire.ai_experience or "",
                questionnaire.years_work_experience or "",
                questionnaire.age or "",
                questionnaire.gender or "",
                questionnaire.industry or "",
                questionnaire.job_role or "",
                questionnaire.timestamp_submit.isoformat() if questionnaire.timestamp_submit else "",
            ])

        buffer.seek(0)
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=questionnaires.csv"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting questionnaires: {str(e)}")


@router.get("/honesty_codings.csv")
def export_honesty_codings(db: Session = Depends(get_db), _: None = Depends(verify_admin_token)) -> StreamingResponse:
    """Export all honesty codings."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, quoting=csv.QUOTE_ALL)
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

    try:
        stmt = (
            select(HonestyCodings, Participant.condition)
            .join(Participant, HonestyCodings.participant_id == Participant.participant_id)
            .order_by(HonestyCodings.participant_id, HonestyCodings.timestamp_coded)
        )

        for coding, condition in db.execute(stmt).all():
            writer.writerow([
                coding.coding_id or "",
                coding.participant_id or "",
                condition or "",
                coding.coder_id or "",
                coding.criticality or "",
                coding.specificity or "",
                coding.riskiness or "",
                coding.feedback_honesty_index or "",
                coding.timestamp_coded.isoformat() if coding.timestamp_coded else "",
                coding.coding_notes or "",
            ])

        buffer.seek(0)
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=honesty_codings.csv"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting honesty codings: {str(e)}")


@router.get("/retrieval_logs.csv")
def export_retrieval_logs(db: Session = Depends(get_db), _: None = Depends(verify_admin_token)) -> StreamingResponse:
    """Export retrieval logs for auditability and reproducibility.

    Note: User messages are stored in the messages table and linked via message_id.
    Retrieval logs contain only aggregate metadata needed for analysis.
    """
    buffer = io.StringIO()
    writer = csv.writer(buffer, quoting=csv.QUOTE_ALL)
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

    try:
        stmt = (
            select(RetrievalLog, Participant.condition)
            .join(Participant, RetrievalLog.participant_id == Participant.participant_id)
            .order_by(RetrievalLog.participant_id, RetrievalLog.turn_index)
        )

        for log, condition in db.execute(stmt).all():
            writer.writerow([
                log.participant_id or "",
                condition or "",
                log.turn_index or "",
                log.message_id or "",
                log.retrieved_card_ids or "",
                log.retrieved_card_constructs or "",
                log.retrieval_scores or "",
                log.retrieval_method or "",
                log.retrieval_enabled or "",
                log.retrieval_top_k or "",
                log.corpus_version or "",
                log.timestamp_created.isoformat() if log.timestamp_created else "",
            ])

        buffer.seek(0)
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=retrieval_logs.csv"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting retrieval logs: {str(e)}")


@router.get("/analysis_dataset.csv")
def export_analysis_dataset(db: Session = Depends(get_db), _: None = Depends(verify_admin_token)) -> StreamingResponse:
    """Export combined analysis dataset: one row per participant with all engagement, perception, and outcome measures."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, quoting=csv.QUOTE_ALL)
    writer.writerow([
        # Participant & condition
        "participant_id",
        "condition",
        # Engagement metrics
        "completed_task",
        "number_user_turns",
        "total_user_word_count",
        "average_user_message_length",
        # Manipulation check (bipolar items)
        "perc_warmth_bipolar",
        "perc_task_focus_bipolar",
        # Psychological safety measures
        "psych_safe_1",
        "psych_safe_2",
        "psych_safe_3",
        "psychological_safety_score",
        # Openness/honesty measures
        "openness_1",
        "openness_2_raw",
        "self_reported_honesty_score",
        # Engagement measure
        "engagement_self_report",
        # Control variables
        "prior_ai_experience",
        "years_work_experience",
        "age",
        "gender",
        "industry",
        "job_role",
    ])

    try:
        participants = db.execute(select(Participant)).scalars().all()
        for participant in participants:
            # Get questionnaire if exists
            questionnaire = db.query(QuestionnaireResponse).filter(
                QuestionnaireResponse.participant_id == participant.participant_id
            ).first()

            writer.writerow([
                # Participant & condition
                participant.participant_id or "",
                participant.condition or "",
                # Engagement metrics
                int(participant.session_completed) if participant.session_completed else "",
                participant.total_turns or "",
                participant.total_user_words or "",
                participant.average_user_message_length or "",
                # Manipulation check (bipolar items)
                questionnaire.perc_warmth_bipolar if questionnaire else "",
                questionnaire.perc_task_focus_bipolar if questionnaire else "",
                # Psychological safety measures
                questionnaire.psych_safe_1 if questionnaire else "",
                questionnaire.psych_safe_2 if questionnaire else "",
                questionnaire.psych_safe_3 if questionnaire else "",
                questionnaire.psychological_safety_mean if questionnaire else "",
                # Openness/honesty measures
                questionnaire.openness_1 if questionnaire else "",
                questionnaire.openness_2 if questionnaire else "",  # Raw value; reverse-code during analysis
                questionnaire.self_reported_honesty_mean if questionnaire else "",
                # Engagement measure
                questionnaire.engagement_self_report if questionnaire else "",
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting analysis dataset: {str(e)}")
