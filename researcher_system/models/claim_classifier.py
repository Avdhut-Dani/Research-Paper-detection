def classify_claim(text):
    if "may" in text.lower() or "could" in text.lower():
        return "weak"
    return "strong"
