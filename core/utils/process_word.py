def process_words(text):
    return [p.strip() for p in text.strip().split(",") if p.strip()]
