import secrets


CONDITIONS = ("warm", "competent")


def assign_condition() -> str:
    return CONDITIONS[secrets.randbelow(len(CONDITIONS))]
