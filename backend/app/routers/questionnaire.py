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

    psych_items = [
        payload.psych_safe_1,
        payload.psych_safe_2,
        payload.psych_safe_3,
        payload.psych_safe_4,
        payload.psych_safe_5,
    ]
    psych_mean = round(sum(psych_items) / len(psych_items), 4)

    row = QuestionnaireResponse(
        participant_id=payload.participant_id,
        manip_warmth_friendly=payload.manip_warmth_friendly,
        manip_warmth_sincere=payload.manip_warmth_sincere,
        manip_competence_competent=payload.manip_competence_competent,
        manip_competence_skilled=payload.manip_competence_skilled,
        psych_safe_1=payload.psych_safe_1,
        psych_safe_2=payload.psych_safe_2,
        psych_safe_3=payload.psych_safe_3,
        psych_safe_4=payload.psych_safe_4,
        psych_safe_5=payload.psych_safe_5,
        psych_safety_mean=psych_mean,
        ai_experience=payload.ai_experience,
        organizational_tenure_years=payload.organizational_tenure_years,
        age=payload.age,
        gender=payload.gender,
        industry=payload.industry,
        job_role=payload.job_role,
    )

    db.add(row)
    participant.questionnaire_completed = True
    participant.session_completed = True
    db.commit()

    return QuestionnaireResponseOut(
        participant_id=participant.id,
        psychological_safety_mean=psych_mean,
        questionnaire_completed=True,
    )
