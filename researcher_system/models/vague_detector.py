VAGUE_WORDS=["many","some","various","several","often"]

def is_vague(text):
    return any(v in text.lower() for v in VAGUE_WORDS)
