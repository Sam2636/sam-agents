# core/tokenizer.py
def count_tokens(text: str) -> int:
    if not text:
        return 0
    # conservative approximation: split on whitespace
    return len(text.split())
