from pydantic import BaseModel, Field
from typing import Optional


class HealthResponse(BaseModel):
    status: str


class StartSessionRequest(BaseModel):
    consented: bool = True
    forced_condition: Optional[str] = None


class StartSessionResponse(BaseModel):
    participant_id: str
    condition: str
    vignette_title: str
    vignette_text: str
    opening_message: str
    min_turns: int
    max_turns: int


class ChatRequest(BaseModel):
    participant_id: str
    message: str = Field(min_length=1, max_length=4000)


class ChatMessageOut(BaseModel):
    role: str
    content: str
    turn_index: int
    follow_up_key: str | None = None


class ChatResponse(BaseModel):
    participant_id: str
    condition: str
    assistant_message: ChatMessageOut
    turns_used: int
    chat_completed: bool


class QuestionnaireRequest(BaseModel):
    participant_id: str
    manip_warmth_friendly: int = Field(ge=1, le=7)
    manip_warmth_sincere: int = Field(ge=1, le=7)
    manip_competence_competent: int = Field(ge=1, le=7)
    manip_competence_skilled: int = Field(ge=1, le=7)
    psych_safe_1: int = Field(ge=1, le=7)
    psych_safe_2: int = Field(ge=1, le=7)
    psych_safe_3: int = Field(ge=1, le=7)
    psych_safe_4: int = Field(ge=1, le=7)
    psych_safe_5: int = Field(ge=1, le=7)
    ai_experience: int = Field(ge=1, le=7)
    organizational_tenure_years: float = Field(ge=0)
    age: int = Field(ge=18, le=100)
    gender: str
    industry: str
    job_role: str


class QuestionnaireResponseOut(BaseModel):
    participant_id: str
    psychological_safety_mean: float
    questionnaire_completed: bool


class ExportTranscriptRow(BaseModel):
    participant_id: str
    condition: str
    role: str
    content: str
    turn_index: int
    word_count: int
    timestamp: str


class HonestyCodeRequest(BaseModel):
    participant_id: str
    coder_id: str
    criticality: int = Field(ge=1, le=5)
    specificity: int = Field(ge=1, le=5)
    riskiness: int = Field(ge=1, le=5)
    coding_notes: Optional[str] = None


class HonestyCodeOut(BaseModel):
    coding_id: str
    participant_id: str
    coder_id: str
    criticality: int
    specificity: int
    riskiness: int
    feedback_honesty_index: float
    coding_notes: Optional[str] = None
    timestamp_coded: str
