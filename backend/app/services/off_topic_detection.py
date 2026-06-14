"""Off-topic and low-quality response detection for participant feedback quality."""

import random
import re
from typing import NamedTuple


class OffTopicResult(NamedTuple):
    is_off_topic: bool
    reason: str | None


def is_off_topic(message: str) -> OffTopicResult:
    """
    Detect if a user message is off-topic, low-quality, or distracted.

    Returns:
        OffTopicResult with is_off_topic flag and reason for logging.
    """
    message = message.strip()

    if not message:
        return OffTopicResult(is_off_topic=True, reason="empty_message")

    # Normalize for analysis (lowercase, remove extra spaces)
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

    # Extremely short (< 3 words) unclear replies
    if word_count < 3:
        return OffTopicResult(is_off_topic=True, reason="too_short")

    # Random unrelated common phrases and topics
    off_topic_phrases = [
        r"^i want(ed)?( to)? (eat|sleep|drink|watch|play)",
        r"^(lol|haha|ha|xd|lmao|rofl)",
        r"^i\s(can't|cannot|could|should|would)(n't)? do (this|it|that)",
        r"^this is (stupid|pointless|waste|bs)",
        r"^(banana|apple|orange|pizza|dog|cat)\b",
        r"^(testing|test|hehe|joke)\b",
        r"^(what about you|tell me about you|how are you)",
        r"^(stop|quit|exit|bye|goodbye)",
        r"^(i'm|my) (hungry|tired|sleepy|angry)",
        r"my (boss|manager|colleague|team)( member)? is my (mom|dad|parent|wife|husband|friend)",
    ]

    if any(re.search(pattern, normalized) for pattern in off_topic_phrases):
        return OffTopicResult(is_off_topic=True, reason="off_topic_phrase")

    # Check for workplace-related keywords
    workplace_keywords = [
        "work", "team", "task", "priority", "assignment", "responsibility",
        "mistake", "unclear", "communication", "manager", "boss", "colleague",
        "feedback", "situation", "problem", "issue", "conflict", "priority",
        "goals", "progress", "deadline", "project", "role", "expectation"
    ]

    # If message is vague and doesn't contain workplace keywords, likely off-topic
    vague_patterns = [
        r"^my (mom|dad|parent|brother|sister|family|friend)",
        r"^(he|she|they|i) (is|are|was|were) (my|their)",
        r"^i (want|need|like|love|hate)",
    ]

    if any(re.match(pattern, normalized) for pattern in vague_patterns):
        if not any(keyword in normalized for keyword in workplace_keywords):
            return OffTopicResult(is_off_topic=True, reason="personal_topic_without_work_context")

    # Self-directed insults without scenario context
    if re.search(r"\b(i'?m stupid|i'm dumb|i'm an idiot|i'm useless|i want to die)\b", normalized):
        # Check if it's actually related to the scenario
        scenario_keywords = [
            "team", "work", "task", "priority", "assignment", "responsibility",
            "mistake", "unclear", "communication", "manager", "boss", "colleague",
            "feedback", "situation", "problem", "issue", "conflict"
        ]
        if not any(keyword in normalized for keyword in scenario_keywords):
            return OffTopicResult(
                is_off_topic=True,
                reason="self_harm_or_insult_without_context"
            )

    # Message is entirely repetitive or doesn't advance the conversation
    if normalized == "i don't know" or normalized == "idk":
        return OffTopicResult(is_off_topic=True, reason="no_effort_response")

    # All caps with exclamation marks (possible trolling) but too short
    if word_count <= 2 and len(re.findall(r"[A-Z!?]", message)) > len(message) * 0.5:
        return OffTopicResult(is_off_topic=True, reason="caps_troll_short")

    return OffTopicResult(is_off_topic=False, reason=None)


def build_redirect_response(condition: str, follow_up_question: str) -> str:
    """
    Build a gentle redirect response to bring participant back on task.

    Args:
        condition: "warm" or "competent" persona
        follow_up_question: The current follow-up question to ask again

    Returns:
        A redirect response that acknowledges and refocuses on the task.
    """
    if condition == "warm":
        acknowledgments = [
            "Got it. ",
            "I hear you. ",
            "Understood. ",
            "Thanks for that. ",
        ]
        redirects = [
            f"Let's get back to the situation you're describing. {follow_up_question}",
            f"I want to focus on what's happening at work. {follow_up_question}",
            f"Let's stay focused on the team situation. {follow_up_question}",
            f"Back to what you mentioned earlier: {follow_up_question}",
        ]
    else:  # competent
        acknowledgments = [
            "Understood. ",
            "Got it. ",
            "Noted. ",
            "I see. ",
        ]
        redirects = [
            f"Let's focus on the workplace situation. {follow_up_question}",
            f"To clarify what's happening at work: {follow_up_question}",
            f"Sticking to the situation at hand: {follow_up_question}",
            f"Let me refocus on the task. {follow_up_question}",
        ]

    ack = random.choice(acknowledgments)
    redir = random.choice(redirects)
    return ack + redir
