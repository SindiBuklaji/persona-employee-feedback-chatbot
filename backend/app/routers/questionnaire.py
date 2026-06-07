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

    # Compute means for perception scales
    warmth_items = [
        payload.perc_warm_warm,
        payload.perc_warm_friendly,
        payload.perc_warm_understanding,
    ]
    perceived_warmth_mean = round(sum(warmth_items) / len(warmth_items), 4)

    competence_items = [
        payload.perc_comp_competent,
        payload.perc_comp_structured,
        payload.perc_comp_capable,
    ]
    perceived_competence_mean = round(sum(competence_items) / len(competence_items), 4)

    # Compute mean for psychological safety
    psych_items = [
        payload.psych_safe_1,
        payload.psych_safe_2,
        payload.psych_safe_3,
        payload.psych_safe_4,
        payload.psych_safe_5,
    ]
    psychological_safety_mean = round(sum(psych_items) / len(psych_items), 4)

    # Compute mean for openness/honesty (with reverse-coding for openness_4)
    # openness_4 is "I held back some things" - reverse code it
    openness_items = [
        payload.openness_1,
        payload.openness_2,
        payload.openness_3,
        (8 - payload.openness_4),  # Reverse code: 1→7, 2→6, ..., 7→1
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
        # Perception items
        perc_warm_warm=payload.perc_warm_warm,
        perc_warm_friendly=payload.perc_warm_friendly,
        perc_warm_understanding=payload.perc_warm_understanding,
        perc_comp_competent=payload.perc_comp_competent,
        perc_comp_structured=payload.perc_comp_structured,
        perc_comp_capable=payload.perc_comp_capable,
        # Psychological safety items
        psych_safe_1=payload.psych_safe_1,
        psych_safe_2=payload.psych_safe_2,
        psych_safe_3=payload.psych_safe_3,
        psych_safe_4=payload.psych_safe_4,
        psych_safe_5=payload.psych_safe_5,
        # Openness/honesty items
        openness_1=payload.openness_1,
        openness_2=payload.openness_2,
        openness_3=payload.openness_3,
        openness_4=payload.openness_4,
        # Computed means
        perceived_warmth_mean=perceived_warmth_mean,
        perceived_competence_mean=perceived_competence_mean,
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
