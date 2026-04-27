def word_count(text: str) -> int:
    """Count words in text by splitting on whitespace."""
    return len([token for token in text.strip().split() if token])


def character_count(text: str) -> int:
    """Count characters in text."""
    return len(text)


def sentence_count(text: str) -> int:
    """Count sentences in text by counting sentence-ending punctuation."""
    # Count periods, exclamation marks, and question marks
    count = text.count('.') + text.count('!') + text.count('?')
    return max(1, count)  # At least 1 if text exists
