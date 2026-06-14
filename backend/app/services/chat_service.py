from __future__ import annotations

import logging
from openai import OpenAI
from sqlalchemy.orm import Session

from app.config import settings
from app.data.vignette import FOLLOW_UP_SEQUENCE, get_follow_up_prompt
from app.models import Message, Participant, RetrievalLog
from app.services.metrics import word_count
from app.services.off_topic_detection import is_off_topic, build_redirect_response
from app.services.personas import get_persona_prompt
from app.services.retrieval import RetrievalService

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.retrieval = RetrievalService()

    def _current_follow_up(self, turns_used: int) -> dict | None:
        if turns_used >= len(FOLLOW_UP_SEQUENCE):
            return None
        return FOLLOW_UP_SEQUENCE[turns_used]

    def _build_retrieval_context(self, docs: list) -> str:
        """Format retrieved documents as hidden background guidance."""
        if not docs:
            return ""

        context_parts = [
            "Relevant research-informed guidance from the fixed retrieval corpus:\n"
        ]

        for i, doc in enumerate(docs, 1):
            context_parts.append(f"\n[Evidence {i}]")
            context_parts.append(f"Construct: {doc.construct if doc.construct else doc.title}")
            context_parts.append(f"Summary: {doc.text.split('Guidance:')[0].strip()[:300]}...")
            if "Guidance:" in doc.text:
                guidance = doc.text.split("Guidance:")[1].strip()[:200]
                context_parts.append(f"Guidance: {guidance}...")

        return "\n".join(context_parts)

    def _build_assistant_reply(
        self,
        condition: str,
        user_message: str,
        turns_used: int,
    ) -> tuple[str, str | None, list[str], list[float], str, list, str | None]:
        """Build assistant reply with retrieval context.

        Returns:
            Tuple of (reply_text, follow_up_key, retrieved_card_ids, retrieval_scores, retrieval_method, retrieved_docs, off_topic_reason)
        """
        next_follow_up = self._current_follow_up(turns_used)

        # Check for off-topic or low-quality messages
        off_topic_result = is_off_topic(user_message)
        if off_topic_result.is_off_topic:
            logger.info(f"Off-topic detection: {off_topic_result.reason}")

            # Get current follow-up question for redirect
            if next_follow_up:
                follow_up_key = next_follow_up["key"]
                follow_up_text = get_follow_up_prompt(condition, follow_up_key)
                redirect_response = build_redirect_response(condition, follow_up_text)
            else:
                # Task complete, just acknowledge gently
                if condition == "warm":
                    redirect_response = "Thanks for that. You've completed the feedback task!"
                else:
                    redirect_response = "Noted. You've completed the feedback task."
                follow_up_key = None

            return (
                redirect_response,
                follow_up_key,
                [],  # No retrieved cards for redirect
                [],  # No scores
                "off_topic_redirect",
                [],  # No docs
                off_topic_result.reason,  # Return the off-topic reason
            )

        retrieved_docs, retrieval_method = self.retrieval.retrieve(user_message)
        retrieval_context = self._build_retrieval_context(retrieved_docs)

        is_complete = next_follow_up is None

        if next_follow_up:
            follow_up_key = next_follow_up["key"]
            follow_up_text = get_follow_up_prompt(condition, follow_up_key)
            completion_instruction = "- End with one clear question to move the conversation forward."
        else:
            follow_up_text = ""
            follow_up_key = None
            completion_instruction = (
                "- Do NOT ask a question. The task is complete. "
                "Acknowledge what the participant shared and end naturally. "
                "Use a closing phrase like 'You have completed the feedback task.' or similar."
            )

        system_prompt = f"""
{get_persona_prompt(condition)}

RESPONSE FORMAT:
- Write 3-5 short sentences. Conversational, not choppy or too short.
- Do NOT repeat the user's exact words. Add one useful angle, distinction, or reframe.
{completion_instruction}
- Sound natural, like a real person talking.

HIDDEN GUIDANCE (not for citing):
{retrieval_context}

{"NEXT QUESTION (continue conversation):" if follow_up_text else "TASK STATUS:"}
{follow_up_text if follow_up_text else "The feedback task is now complete. Do not ask another question."}

CRITICAL RULES:
- Do NOT mention sources, corpus, research, or theory.
- Do NOT use academic language: contributing factors, dynamics, inhibit, stakeholders, environment.
- Do NOT say "This may indicate...", "This can create challenges...", "Let's explore", or similar phrases.
- Do NOT validate vague or harsh claims as facts. Ask for specifics instead.
- Do NOT use the same opening phrase repeatedly (e.g., "It sounds like", "That sounds").
- Do NOT start with emotional validation if you did that in the previous response.
- When user makes a vague claim (e.g., "they don't care"), ask for clarification, not agreement.
- If user makes a harsh claim (e.g., "management is bad"), ask for concrete examples.

VARIED OPENING PHRASES (warm):
"I get why that would bother you." / "That would be hard to deal with." / "That's a lot to carry." / "I can see why you'd hesitate." / "That would be really frustrating." / "That's a fair concern."

VARIED OPENING PHRASES (competent):
"That points to..." / "The issue seems to be..." / "A useful distinction is..." / "To make this concrete..." / "Before we assume that, let's clarify..." / "The key concern is..."

If off-topic, respond briefly and redirect gently.
""".strip()

        user_prompt = f"""
Participant message:
{user_message}

Write the assistant reply for the assigned condition.

INSTRUCTIONS:
- If the message is clearly on-topic (about the workplace feedback scenario), respond appropriately.
{"- Include the exact follow-up question provided in the system prompt to continue the conversation." if not is_complete else "- Do NOT ask a follow-up question. Acknowledge completion and end naturally."}
- If off-topic, unclear, or testing/critiquing (e.g., "you are being mean"), respond briefly and empathetically without asking a follow-up. Gently redirect if appropriate.
- Always maintain the assigned persona (warm or competent).
""".strip()

        try:
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=settings.temperature,
            )
            text = response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise

        retrieved_card_ids = [doc.doc_id for doc in retrieved_docs]
        retrieval_scores = [doc.score for doc in retrieved_docs]

        return text, follow_up_key, retrieved_card_ids, retrieval_scores, retrieval_method, retrieved_docs, None

    def process_user_message(self, db: Session, participant: Participant, user_message: str) -> Message:
        from datetime import datetime
        from app.services.metrics import character_count, sentence_count

        turn_index = participant.total_turns + 1
        user_word_count = word_count(user_message)

        # Save user message
        user_msg_obj = Message(
            participant_id=participant.participant_id,
            role="user",
            content=user_message,
            turn_index=turn_index,
            turn_index_user_only=turn_index,
            word_count=user_word_count,
            character_count=character_count(user_message),
            sentence_count=sentence_count(user_message),
            timestamp_created=datetime.utcnow(),
        )
        db.add(user_msg_obj)
        db.flush()  # Get message_id

        participant.total_turns += 1
        participant.total_user_words += user_word_count

        # Get the user message to calculate response latency
        user_message_time = datetime.utcnow()

        # Build assistant reply with retrieval
        assistant_text, follow_up_key, retrieved_card_ids, retrieval_scores, retrieval_method, retrieved_docs, off_topic_reason = (
            self._build_assistant_reply(
                condition=participant.condition,
                user_message=user_message,
                turns_used=participant.total_turns,
            )
        )

        assistant_word_count = word_count(assistant_text)
        assistant_message_time = datetime.utcnow()
        response_latency = (assistant_message_time - user_message_time).total_seconds()

        assistant_message = Message(
            participant_id=participant.participant_id,
            role="assistant",
            content=assistant_text,
            turn_index=turn_index,
            turn_index_assistant_only=turn_index,
            word_count=assistant_word_count,
            character_count=character_count(assistant_text),
            sentence_count=sentence_count(assistant_text),
            response_latency_seconds=response_latency,
            timestamp_created=assistant_message_time,
            follow_up_key=follow_up_key,
            model_used=settings.openai_model,
            temperature=settings.temperature,
            is_off_topic_redirect=off_topic_reason is not None,
            off_topic_reason=off_topic_reason,
        )
        db.add(assistant_message)
        db.flush()

        # Log retrieval metadata if enabled
        if settings.retrieval_logging_enabled:
            retrieval_log = RetrievalLog(
                participant_id=participant.participant_id,
                message_id=assistant_message.message_id,
                turn_index=turn_index,
                retrieved_card_ids=",".join(retrieved_card_ids) if retrieved_card_ids else "",
                retrieved_card_constructs="; ".join([doc.construct or f"Doc {i}" for i, doc in enumerate(retrieved_docs, 1)]) if retrieved_docs else "",
                retrieval_scores=",".join(f"{score:.4f}" for score in retrieval_scores) if retrieval_scores else "",
                retrieval_method=retrieval_method,
                retrieval_top_k=settings.top_k_retrieval,
                retrieval_enabled=settings.retrieval_enabled,
                corpus_version="1.0",
            )
            db.add(retrieval_log)

        participant.total_assistant_words += assistant_word_count
        db.commit()
        db.refresh(assistant_message)
        return assistant_message
