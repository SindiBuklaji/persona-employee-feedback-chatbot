from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Participant(Base):
    __tablename__ = "participants"

    participant_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Consent & Condition
    consent_given: Mapped[bool] = mapped_column(Boolean, default=False)
    condition: Mapped[str] = mapped_column(String, nullable=False)
    forced_condition: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    timestamp_session_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    timestamp_chat_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    timestamp_chat_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    timestamp_questionnaire_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    timestamp_questionnaire_submit: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Completion Status
    completion_stage: Mapped[str] = mapped_column(String, default="consent")  # consent, vignette, chat, questionnaire, completed
    dropout_stage: Mapped[str | None] = mapped_column(String, nullable=True)
    chat_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    questionnaire_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    session_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Engagement Metrics
    total_turns: Mapped[int] = mapped_column(Integer, default=0)
    total_user_words: Mapped[int] = mapped_column(Integer, default=0)
    total_assistant_words: Mapped[int] = mapped_column(Integer, default=0)

    messages: Mapped[list["Message"]] = relationship(back_populates="participant", cascade="all, delete-orphan")
    questionnaire: Mapped["QuestionnaireResponse | None"] = relationship(
        back_populates="participant",
        cascade="all, delete-orphan",
        uselist=False,
    )
    honesty_codings: Mapped[list["HonestyCodings"]] = relationship(back_populates="participant", cascade="all, delete-orphan")
    retrieval_logs: Mapped[list["RetrievalLog"]] = relationship(back_populates="participant", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    message_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    participant_id: Mapped[str] = mapped_column(ForeignKey("participants.participant_id"), nullable=False)

    # Message Content & Role
    role: Mapped[str] = mapped_column(String, nullable=False)  # 'user' or 'assistant'
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Indexing (separate counters for user vs assistant)
    turn_index: Mapped[int] = mapped_column(Integer, nullable=False)  # Overall message index
    turn_index_user_only: Mapped[int | None] = mapped_column(Integer, nullable=True)  # User message counter
    turn_index_assistant_only: Mapped[int | None] = mapped_column(Integer, nullable=True)  # Assistant message counter

    # Timestamps
    timestamp_created: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    response_latency_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)  # Only for assistant messages

    # Content Metrics
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    character_count: Mapped[int] = mapped_column(Integer, default=0)
    sentence_count: Mapped[int] = mapped_column(Integer, default=0)

    # Context
    follow_up_key: Mapped[str | None] = mapped_column(String, nullable=True)  # opening, issue_detail, impact, causes, improvement

    # Model Info (for assistant messages)
    model_used: Mapped[str | None] = mapped_column(String, nullable=True)
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)

    participant: Mapped[Participant] = relationship(back_populates="messages")
    retrieval_log: Mapped["RetrievalLog | None"] = relationship(back_populates="message", uselist=False)


class QuestionnaireResponse(Base):
    __tablename__ = "questionnaire_responses"

    response_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    participant_id: Mapped[str] = mapped_column(ForeignKey("participants.participant_id"), unique=True, nullable=False)

    # Timestamps
    timestamp_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)  # When form loads
    timestamp_submit: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)  # When submitted
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Psychological Safety (5 items, 1-7 scale)
    psych_safe_1: Mapped[int] = mapped_column(Integer)
    psych_safe_2: Mapped[int] = mapped_column(Integer)
    psych_safe_3: Mapped[int] = mapped_column(Integer)
    psych_safe_4: Mapped[int] = mapped_column(Integer)
    psych_safe_5: Mapped[int] = mapped_column(Integer)
    psychological_safety_mean: Mapped[float] = mapped_column(Float)

    # Manipulation Checks (1-7 scale)
    manip_warmth_friendly: Mapped[int] = mapped_column(Integer)
    manip_warmth_sincere: Mapped[int] = mapped_column(Integer)
    manip_competence_competent: Mapped[int] = mapped_column(Integer)
    manip_competence_skilled: Mapped[int] = mapped_column(Integer)

    # Demographics & Covariates
    ai_experience: Mapped[int] = mapped_column(Integer)
    organizational_tenure_years: Mapped[float] = mapped_column(Float)
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[str] = mapped_column(String)
    industry: Mapped[str] = mapped_column(String)
    job_role: Mapped[str] = mapped_column(String)

    participant: Mapped[Participant] = relationship(back_populates="questionnaire")


class HonestyCodings(Base):
    __tablename__ = "honesty_codings"
    __table_args__ = (UniqueConstraint("participant_id", "coder_id"),)

    coding_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    participant_id: Mapped[str] = mapped_column(ForeignKey("participants.participant_id"), nullable=False)
    coder_id: Mapped[str] = mapped_column(String, nullable=False)

    # Feedback Honesty Dimensions (1-5 scale each)
    criticality: Mapped[int] = mapped_column(Integer, nullable=False)  # Intensity of problem evaluation
    specificity: Mapped[int] = mapped_column(Integer, nullable=False)  # Concrete detail vs vague
    riskiness: Mapped[int] = mapped_column(Integer, nullable=False)  # Challenges established practices

    # Composite
    feedback_honesty_index: Mapped[float] = mapped_column(Float, nullable=False)

    # Metadata
    coding_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp_coded: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    participant: Mapped[Participant] = relationship(back_populates="honesty_codings")


class RetrievalLog(Base):
    __tablename__ = "retrieval_logs"

    log_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    participant_id: Mapped[str] = mapped_column(ForeignKey("participants.participant_id"), nullable=False)
    message_id: Mapped[str] = mapped_column(ForeignKey("messages.message_id"), nullable=False)
    turn_index: Mapped[int] = mapped_column(Integer, nullable=False)

    # Retrieved Cards (stored as comma-separated IDs)
    retrieved_card_ids: Mapped[str] = mapped_column(String, nullable=False)  # e.g., "psych_safety_001,org_silence_002,..."
    retrieved_card_constructs: Mapped[str] = mapped_column(Text, nullable=False)  # e.g., "construct1; construct2; ..."

    # Retrieval Details
    retrieval_scores: Mapped[str] = mapped_column(String, nullable=False)  # e.g., "0.85,0.72,0.68"
    retrieval_method: Mapped[str] = mapped_column(String, nullable=False)  # "embedding", "keyword_fallback", "disabled"
    retrieval_top_k: Mapped[int] = mapped_column(Integer, nullable=False)
    retrieval_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    corpus_version: Mapped[str] = mapped_column(String, default="1.0")  # For reproducibility

    # Timestamps
    timestamp_created: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    participant: Mapped[Participant] = relationship(back_populates="retrieval_logs")
    message: Mapped[Message] = relationship(back_populates="retrieval_log")
