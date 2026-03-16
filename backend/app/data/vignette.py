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

# These follow-up prompts must stay substantively identical across conditions.
FOLLOW_UP_SEQUENCE = [
    {
        "key": "issue_detail",
        "prompt": "What exactly is happening in this situation? Please describe the main issue as concretely as possible.",
    },
    {
        "key": "impact",
        "prompt": "How does this issue affect your work, motivation, or the team’s functioning?",
    },
    {
        "key": "causes",
        "prompt": "What do you think are the main causes or contributing factors behind this problem?",
    },
    {
        "key": "improvement",
        "prompt": "What changes or actions would most improve this situation? Please be as specific as possible.",
    },
]
