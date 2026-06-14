"""Off-topic and low-quality response detection for participant feedback quality."""

import random
import re
from typing import NamedTuple


class OffTopicResult(NamedTuple):
    is_off_topic: bool
    reason: str | None


def classify_message(message: str) -> str:
    """
    Classify a message as: on_topic | unclear_potentially_on_topic | off_topic

    Returns:
        Classification string.
    """
    message = message.strip()
    normalized = " ".join(message.lower().split())
    words = normalized.split()
    word_count = len(words)

    # Clearly off-topic patterns (unrelated topics, trolling, etc.)
    clearly_off_topic_patterns = [
        r"^(lol|haha|ha|xd|lmao|rofl)$",
        r"^(banana|apple|orange|pizza|dog|cat|food|eat|sleep|drink|joke|weather)$",
        r"^i (want|wanna|gonna) (eat|sleep|drink|play|watch)",
        r"^(tell me a joke|what'?s the weather|hello there|hi there)$",
        r"^random|^test|^testing$|^hehe$|^bye$|^goodbye$|^stop$|^quit$",
        r"^i like (food|pizza|cats|dogs|games)",
        r"^what is the (weather|time|date)",
    ]

    if any(re.search(pattern, normalized) for pattern in clearly_off_topic_patterns):
        return "off_topic"

    # Emotional/workplace-related terms that indicate ON-TOPIC messages
    # These are valid workplace feedback even if vague
    workplace_emotional_terms = [
        "neglected", "ignored", "excluded", "not listened", "not taken seriously",
        "unfair", "recognized", "appreciated", "heard", "valued", "safe", "speaking",
        "spoke", "answered", "answers", "input", "feedback", "confidential", "opinion",
        "ideas", "suggestions", "frustrated", "annoyed", "confused", "uncertain",
        "unclear", "misunderstood", "undervalued", "overworked", "overwhelmed",
        "concerned", "worried", "stressed", "anxious", "uncertain", "unheard"
    ]

    has_emotional_term = any(re.search(rf"\b{term}\b", normalized) for term in workplace_emotional_terms)

    # Direct workplace terms
    direct_workplace_terms = [
        "work", "team", "task", "priority", "assignment", "responsibility",
        "mistake", "communication", "manager", "boss", "colleague", "feedback",
        "situation", "problem", "issue", "conflict", "deadline", "project", "role",
        "expectation", "instruction", "coordination", "meeting", "input", "meeting"
    ]

    has_work_term = any(re.search(rf"\b{term}\b", normalized) for term in direct_workplace_terms)

    # If message has emotional/workplace terms, it's ON-TOPIC
    if has_emotional_term or has_work_term:
        return "on_topic"

    # Unclear but potentially on-topic (feeling bad, hard, tired, annoying, etc.)
    unclear_patterns = [
        r"\b(feel|feels|feeling)\b",
        r"\b(hard|difficult|tough|challenging)\b",
        r"\b(annoyed|annoying|irritating|bothering)\b",
        r"\b(tired|exhausted|drained)\b",
        r"\b(bad|awful|terrible|horrible)\b",
        r"\b(not good|not great)\b",
    ]

    if any(re.search(pattern, normalized) for pattern in unclear_patterns):
        return "unclear_potentially_on_topic"

    # Short personal narratives without workplace context (went to shop, saw cat, etc.)
    personal_narrative_patterns = [
        r"^(today|yesterday|last week|i|my)",
        r"\b(went|saw|visited|did|was|were)\b"
    ]

    if word_count >= 3 and any(re.search(pattern, normalized) for pattern in personal_narrative_patterns):
        if not has_emotional_term and not has_work_term:
            return "off_topic"

    # Default: if message has no clear markers, assume on-topic (be conservative)
    return "on_topic"


def is_off_topic(message: str) -> OffTopicResult:
    """
    Detect if a user message is off-topic, low-quality, or distracted.

    Returns:
        OffTopicResult with is_off_topic flag and reason for logging.
    """
    message = message.strip()

    if not message:
        return OffTopicResult(is_off_topic=True, reason="empty_message")

    normalized = " ".join(message.lower().split())
    words = normalized.split()
    word_count = len(words)

    # Very short greetings only
    if word_count <= 2:
        greeting_patterns = [
            "^(hi|hey|hello|yo|what'?s up|sup|howdy)$",
            "^(thanks|thank you|ok|okay|sure|nope|no|yes|yep)$",
        ]
        if any(re.match(pattern, normalized) for pattern in greeting_patterns):
            return OffTopicResult(is_off_topic=True, reason="greeting_only")

    # Extremely short replies
    if word_count < 3:
        return OffTopicResult(is_off_topic=True, reason="too_short")

    # Self-harm language
    if re.search(r"\b(i'?m stupid|i'm dumb|i'm an idiot|i'm useless|i want to die)\b", normalized):
        return OffTopicResult(is_off_topic=True, reason="self_harm_or_insult")

    # "I don't know" without elaboration
    if normalized in ("i don't know", "idk", "no idea"):
        return OffTopicResult(is_off_topic=True, reason="no_effort_response")

    # Use the classification function
    classification = classify_message(message)

    if classification == "off_topic":
        return OffTopicResult(is_off_topic=True, reason="clearly_off_topic")

    # Unclear but potentially on-topic messages are NOT off-topic
    # They should get a clarifying question from the LLM instead
    return OffTopicResult(is_off_topic=False, reason=None)


def build_redirect_response(condition: str, follow_up_question: str) -> str:
    """
    Build a redirect response for clearly off-topic messages.

    Args:
        condition: "warm" or "competent" persona
        follow_up_question: The current follow-up question to ask again

    Returns:
        A redirect response that refocuses on the task.
    """
    if condition == "warm":
        responses = [
            f"Let's stay focused on the workplace situation. {follow_up_question}",
            f"I want to understand what's happening at work. {follow_up_question}",
            f"Can we focus on the team situation? {follow_up_question}",
        ]
    else:  # competent
        responses = [
            f"Let's focus on the workplace situation. {follow_up_question}",
            f"Please answer based on the work scenario. {follow_up_question}",
            f"Sticking to the situation at hand: {follow_up_question}",
        ]

    return random.choice(responses)
