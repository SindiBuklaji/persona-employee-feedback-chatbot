VIGNETTE_TITLE = "Your Team Situation"

VIGNETTE_TEXT = """
Imagine you are a junior team member or intern. Over the past few weeks, you've noticed some issues:

- Tasks are assigned at the last minute
- Priorities change without explanation
- Responsibilities aren't always clear
- Important information comes too late
- Different people give conflicting instructions
- Work sometimes gets duplicated

Because you're newer to the team, you're not sure how to bring these up directly.

---

**Please give feedback as if you were in this situation. There are no right or wrong answers. Respond naturally and honestly.**

In the chat, please:
- Describe what you think is going wrong
- Give examples if relevant
- Suggest what should change
""".strip()

# Core follow-up sequence: same constructs, different phrasings by condition
FOLLOW_UP_SEQUENCE = [
    {
        "key": "issue_detail",
        "warm": "What’s going on? Tell me what you’re seeing.",
        "competent": "What’s the main issue you’re seeing?",
    },
    {
        "key": "impact",
        "warm": "How’s it affecting you?",
        "competent": "What impact does that have on your work or the team?",
    },
    {
        "key": "causes",
        "warm": "What do you think is behind it?",
        "competent": "What do you think is the root cause?",
    },
    {
        "key": "improvement",
        "warm": "What would help?",
        "competent": "What would fix it?",
    },
    {
        "key": "reflection",
        "warm": "Is there anything else you’d like to add about this situation?",
        "competent": "Is there anything else important you’d like to add?",
    },
]


def get_follow_up_prompt(condition: str, follow_up_key: str) -> str:
    """Get persona-specific wording for follow-up questions."""
    for item in FOLLOW_UP_SEQUENCE:
        if item["key"] == follow_up_key:
            return item.get(condition, item.get("warm", ""))
    return ""
