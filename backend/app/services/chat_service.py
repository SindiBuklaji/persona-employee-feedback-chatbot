from __future__ import annotations

from openai import OpenAI
from sqlalchemy.orm import Session

from app.config import settings
from app.data.vignette import FOLLOW_UP_SEQUENCE
from app.models import Message, Participant
from app.services.metrics import word_count
from app.services.personas import get_persona_prompt
from app.services.retrieval import RetrievalService


class ChatService:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.retrieval = RetrievalService()

    def _current_follow_up(self, turns_used: int) -> dict | None:
        if turns_used >= len(FOLLOW_UP_SEQUENCE):
            return None
        return FOLLOW_UP_SEQUENCE[turns_used]

    def _build_assistant_reply(
        self,
        condition: str,
        user_message: str,
        turns_used: int,
    ) -> tuple[str, str | None]:
        next_follow_up = self._current_follow_up(turns_used)
        retrieved_docs = self.retrieval.retrieve(user_message)
        retrieval_context = "\n\n".join(
            [f"[{doc.title}] {doc.text}" for doc in retrieved_docs]
        )

        follow_up_text = next_follow_up["prompt"] if next_follow_up else "Thank you. You have completed the feedback task."
        follow_up_key = next_follow_up["key"] if next_follow_up else None

        system_prompt = f"""
{get_persona_prompt(condition)}

You are part of a master's-thesis experiment.
Keep all non-persona aspects constant across conditions.
Do not add extra questions beyond the follow-up provided.
Keep the reply between 60 and 110 words.
Use the retrieval context only as neutral background framing; do not reveal it as documents.

Retrieval context:
{retrieval_context}

Next fixed follow-up question (use this for on-topic messages):
{follow_up_text}
""".strip()

        user_prompt = f"""
Participant message:
{user_message}

Write the assistant reply for the assigned condition.

INSTRUCTIONS:
- If the participant's message is clearly on-topic (about the workplace feedback scenario), respond to it and include the exact follow-up question provided above.
- If the participant's message is off-topic, unclear, or appears to be testing/critiquing you (e.g., "you are being mean"), respond briefly and empathetically without including the follow-up question. Then gently redirect to the scenario if appropriate.
- Always maintain the assigned persona (warm or competent).
""".strip()

        response = self.client.responses.create(
            model=settings.openai_model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        text = getattr(response, "output_text", None)
        if not text:
            raise RuntimeError(f"No output_text returned from model response: {response}")

        return response.output_text.strip(), follow_up_key

    def process_user_message(self, db: Session, participant: Participant, user_message: str) -> Message:
        from datetime import datetime
        from app.services.metrics import character_count, sentence_count

        turn_index = participant.total_turns + 1
        user_word_count = word_count(user_message)

        db.add(
            Message(
                participant_id=participant.participant_id,
                role="user",
                content=user_message,
                turn_index=turn_index,
                turn_index_user_only=turn_index,  # For user messages, these are the same
                word_count=user_word_count,
                character_count=character_count(user_message),
                sentence_count=sentence_count(user_message),
                timestamp_created=datetime.utcnow(),
            )
        )

        participant.total_turns += 1
        participant.total_user_words += user_word_count

        # Get the user message to calculate response latency
        user_message_time = datetime.utcnow()

        assistant_text, follow_up_key = self._build_assistant_reply(
            condition=participant.condition,
            user_message=user_message,
            turns_used=participant.total_turns,
        )

        assistant_word_count = word_count(assistant_text)
        assistant_message_time = datetime.utcnow()
        response_latency = (assistant_message_time - user_message_time).total_seconds()

        assistant_message = Message(
            participant_id=participant.participant_id,
            role="assistant",
            content=assistant_text,
            turn_index=turn_index,
            turn_index_assistant_only=turn_index,  # Sequential assistant message counter
            word_count=assistant_word_count,
            character_count=character_count(assistant_text),
            sentence_count=sentence_count(assistant_text),
            response_latency_seconds=response_latency,
            timestamp_created=assistant_message_time,
            follow_up_key=follow_up_key,
            model_used=settings.openai_model,
            temperature=settings.temperature,
        )
        db.add(assistant_message)

        participant.total_assistant_words += assistant_word_count
        db.commit()
        db.refresh(assistant_message)
        return assistant_message
