VIGNETTE_TITLE = "Workplace feedback scenario"

VIGNETTE_TEXT = """
Imagine that you are a working student or early-career employee in a team where workload is unevenly distributed.
Over the last few weeks, you have repeatedly had to take over urgent tasks because responsibilities were unclear.
At the same time, internal communication has been inconsistent, and your manager often changes priorities at short notice.
This has led to stress, frustration, and the feeling that problems are not addressed openly.

You are now asked to provide honest written feedback through an AI-based feedback assistant.
Please describe the issue as candidly and specifically as you can, including what is happening, why it is problematic,
and what could be improved.
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
