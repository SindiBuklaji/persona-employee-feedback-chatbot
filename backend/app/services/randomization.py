import secrets


CONDITIONS = ("warm", "competent")


def assign_condition(warm_count: int = 0, competent_count: int = 0) -> str:
    """
    Assign condition using minimization algorithm.
    Favors the condition with fewer participants to maintain balance.

    Args:
        warm_count: Current number of warm condition participants
        competent_count: Current number of competent condition participants

    Returns:
        "warm" or "competent"
    """
    diff = warm_count - competent_count

    if diff < 0:  # More competent assigned, favor warm (90% chance)
        return "warm" if secrets.randbelow(100) < 90 else "competent"
    elif diff > 0:  # More warm assigned, favor competent (90% chance)
        return "competent" if secrets.randbelow(100) < 90 else "warm"
    else:  # Equal, 50/50
        return secrets.choice(CONDITIONS)
