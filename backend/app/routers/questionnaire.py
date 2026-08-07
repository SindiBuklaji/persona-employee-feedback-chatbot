from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Participant, QuestionnaireResponse
from app.schemas import QuestionnaireRequest, QuestionnaireResponseOut

router = APIRouter(prefix="/questionnaire", tags=["questionnaire"])


@router.post("", response_model=QuestionnaireResponseOut)
def submit_questionnaire(payload: QuestionnaireRequest, db: Session = Depends(get_db)) -> QuestionnaireResponseOut:
    participant = db.get(Participant, payload.participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found.")
    if not participant.chat_completed:
        raise HTTPException(status_code=400, detail="Chat must be completed first.")
    if participant.questionnaire_completed:
        raise HTTPException(status_code=400, detail="Questionnaire already submitted.")

    # Manipulation check (bipolar sliders) - no means needed, just store raw values
    # These are diagnostic checks, not dependent variables

    # Compute mean for psychological safety (3 items)
    psych_items = [
        payload.psych_safe_1,
        payload.psych_safe_2,
        payload.psych_safe_3,
    ]
    psychological_safety_mean = round(sum(psych_items) / len(psych_items), 4)

    # Compute mean for openness/honesty (2 items with reverse-coding for openness_2)
    # openness_2 is "I held back some things" - reverse code it
    openness_items = [
        payload.openness_1,
        (8 - payload.openness_2),  # Reverse code: 1→7, 2→6, ..., 7→1
    ]
    self_reported_honesty_mean = round(sum(openness_items) / len(openness_items), 4)

    # Compute warmth composite (Synthetic v2 only) - mean of warmth_1-4
    perceived_warmth_mean = None
    if all([payload.warmth_1, payload.warmth_2, payload.warmth_3, payload.warmth_4]):
        warmth_items = [payload.warmth_1, payload.warmth_2, payload.warmth_3, payload.warmth_4]
        perceived_warmth_mean = round(sum(warmth_items) / len(warmth_items), 4)

    # Compute competence composite (Synthetic v2 only) - mean of competence_1-4
    perceived_competence_mean = None
    if all([payload.competence_1, payload.competence_2, payload.competence_3, payload.competence_4]):
        competence_items = [payload.competence_1, payload.competence_2, payload.competence_3, payload.competence_4]
        perceived_competence_mean = round(sum(competence_items) / len(competence_items), 4)

    # Compute sincerity composite (Synthetic v2 only) - mean of sincerity_1, (8-sincerity_2), sincerity_3
    sincerity_mean = None
    if all([payload.sincerity_1, payload.sincerity_2, payload.sincerity_3]):
        sincerity_items = [
            payload.sincerity_1,
            (8 - payload.sincerity_2),  # Reverse code: 1→7, 2→6, ..., 7→1
            payload.sincerity_3,
        ]
        sincerity_mean = round(sum(sincerity_items) / len(sincerity_items), 4)

    # Compute average user message length
    if participant.total_turns > 0:
        average_user_message_length = round(participant.total_user_words / participant.total_turns, 2)
    else:
        average_user_message_length = None

    now = datetime.utcnow()
    row = QuestionnaireResponse(
        participant_id=payload.participant_id,
        timestamp_submit=now,
        # Manipulation check (bipolar items)
        perc_warmth_bipolar=payload.perc_warmth_bipolar,
        perc_task_focus_bipolar=payload.perc_task_focus_bipolar,
        # Psychological safety items
        psych_safe_1=payload.psych_safe_1,
        psych_safe_2=payload.psych_safe_2,
        psych_safe_3=payload.psych_safe_3,
        # Openness/honesty items
        openness_1=payload.openness_1,
        openness_2=payload.openness_2,
        # Engagement item
        engagement_self_report=payload.engagement_self_report,
        # Warmth composite (Synthetic v2 only)
        warmth_1=payload.warmth_1,
        warmth_2=payload.warmth_2,
        warmth_3=payload.warmth_3,
        warmth_4=payload.warmth_4,
        # Competence composite (Synthetic v2 only)
        competence_1=payload.competence_1,
        competence_2=payload.competence_2,
        competence_3=payload.competence_3,
        competence_4=payload.competence_4,
        # Sincerity composite (Synthetic v2 only)
        sincerity_1=payload.sincerity_1,
        sincerity_2=payload.sincerity_2,
        sincerity_3=payload.sincerity_3,
        # Computed means
        perceived_warmth_mean=perceived_warmth_mean,
        perceived_competence_mean=perceived_competence_mean,
        sincerity_mean=sincerity_mean,
        psychological_safety_mean=psychological_safety_mean,
        self_reported_honesty_mean=self_reported_honesty_mean,
        # Control variables
        ai_experience=payload.ai_experience,
        years_work_experience=payload.years_work_experience,
        age=payload.age,
        gender=payload.gender,
        industry=payload.industry,
        job_role=payload.job_role,
    )

    db.add(row)
    participant.questionnaire_completed = True
    participant.session_completed = True
    participant.completion_stage = "completed"
    participant.timestamp_questionnaire_submit = now
    participant.average_user_message_length = average_user_message_length
    db.commit()

    return QuestionnaireResponseOut(
        participant_id=participant.participant_id,
        psychological_safety_mean=psychological_safety_mean,
        questionnaire_completed=True,
    )
