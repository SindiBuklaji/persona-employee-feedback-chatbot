def word_count(text: str) -> int:
    return len([token for token in text.strip().split() if token])
