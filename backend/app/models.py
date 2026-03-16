from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Participant(Base):
    __tablename__ = "participants"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    consented: Mapped[bool] = mapped_column(Boolean, default=False)
    condition: Mapped[str] = mapped_column(String, nullable=False)
    session_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    chat_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    questionnaire_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    total_turns: Mapped[int] = mapped_column(Integer, default=0)
    total_user_words: Mapped[int] = mapped_column(Integer, default=0)
    started_chat_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_chat_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    messages: Mapped[list["Message"]] = relationship(back_populates="participant", cascade="all, delete-orphan")
    questionnaire: Mapped["QuestionnaireResponse | None"] = relationship(
        back_populates="participant",
        cascade="all, delete-orphan",
        uselist=False,
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    participant_id: Mapped[str] = mapped_column(ForeignKey("participants.id"), nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    turn_index: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    follow_up_key: Mapped[str | None] = mapped_column(String, nullable=True)

    participant: Mapped[Participant] = relationship(back_populates="messages")


class QuestionnaireResponse(Base):
    __tablename__ = "questionnaire_responses"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    participant_id: Mapped[str] = mapped_column(ForeignKey("participants.id"), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    manip_warmth_friendly: Mapped[int] = mapped_column(Integer)
    manip_warmth_sincere: Mapped[int] = mapped_column(Integer)
    manip_competence_competent: Mapped[int] = mapped_column(Integer)
    manip_competence_skilled: Mapped[int] = mapped_column(Integer)

    psych_safe_1: Mapped[int] = mapped_column(Integer)
    psych_safe_2: Mapped[int] = mapped_column(Integer)
    psych_safe_3: Mapped[int] = mapped_column(Integer)
    psych_safe_4: Mapped[int] = mapped_column(Integer)
    psych_safe_5: Mapped[int] = mapped_column(Integer)
    psych_safety_mean: Mapped[float] = mapped_column(Float)

    ai_experience: Mapped[int] = mapped_column(Integer)
    organizational_tenure_years: Mapped[float] = mapped_column(Float)
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[str] = mapped_column(String)
    industry: Mapped[str] = mapped_column(String)
    job_role: Mapped[str] = mapped_column(String)

    participant: Mapped[Participant] = relationship(back_populates="questionnaire")
