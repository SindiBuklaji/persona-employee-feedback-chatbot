VIGNETTE_TITLE = "Giving Feedback About Workload and Team Coordination"

VIGNETTE_TEXT = """
Imagine you are a working student, intern, or early-career employee in a team. Over the past several weeks, tasks have often been assigned at short notice, priorities have changed without explanation, and responsibilities have not always been clearly defined. As a result, work is sometimes duplicated, deadlines are harder to meet, and you often end up taking on extra tasks to make sure things are completed.

Communication in the team is also inconsistent. Important information is sometimes shared too late, different people give conflicting instructions, and it is often unclear who is responsible for final decisions. You feel that these issues are affecting both team performance and your own work experience, but because you are in a relatively junior position, you are unsure how directly to raise these concerns.

Please provide feedback as if this input could be reviewed by people responsible for improving team processes.

In the chat, please:

- describe what you think is going wrong,

- give examples if relevant,

- suggest what should change.
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
]


def get_follow_up_prompt(condition: str, follow_up_key: str) -> str:
    """Get persona-specific wording for follow-up questions."""
    for item in FOLLOW_UP_SEQUENCE:
        if item["key"] == follow_up_key:
            return item.get(condition, item.get("warm", ""))
    return ""
