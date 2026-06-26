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

    # PERCEPTION: How did you perceive the assistant? (1-7 scale)
    # Warmth
    perc_warm_friendly: int = Field(ge=1, le=7)
    perc_warm_understanding: int = Field(ge=1, le=7)
    perc_warm_comfortable: int = Field(ge=1, le=7)
    # Structured/Direct
    perc_struct_direct: int = Field(ge=1, le=7)
    perc_struct_professional: int = Field(ge=1, le=7)
    perc_struct_task_focused: int = Field(ge=1, le=7)

    # PSYCHOLOGICAL SAFETY: How safe did you feel during the conversation? (1-7 scale)
    psych_safe_1: int = Field(ge=1, le=7)
    psych_safe_2: int = Field(ge=1, le=7)
    psych_safe_3: int = Field(ge=1, le=7)
    psych_safe_4: int = Field(ge=1, le=7)
    psych_safe_5: int = Field(ge=1, le=7)

    # OPENNESS/HONESTY: How openly did you respond? (1-7 scale)
    openness_1: int = Field(ge=1, le=7)
    openness_2: int = Field(ge=1, le=7)
    openness_3: int = Field(ge=1, le=7)
    openness_4: int = Field(ge=1, le=7)

    # CONTROL VARIABLES
    ai_experience: int = Field(ge=1, le=7, description="Prior conversational AI experience")
    years_work_experience: Optional[float] = Field(None, ge=0, description="Total years of work experience")
    age: Optional[int] = Field(None, ge=18, le=100, description="Age (optional)")
    gender: Optional[str] = Field(None, description="Gender (optional)")
    industry: Optional[str] = Field(None, description="Industry (optional)")
    job_role: Optional[str] = Field(None, description="Job role (optional)")


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
