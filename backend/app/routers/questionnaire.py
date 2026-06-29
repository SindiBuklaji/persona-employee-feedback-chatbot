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
        # Computed means
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
