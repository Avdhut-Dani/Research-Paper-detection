import spacy
nlp = spacy.load("en_core_web_sm")

def split_sentences(text):
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents]

def extract_claims(text):
    # This is now a wrapper that uses split_sentences
    # The actual semantic filtering happens in the pipeline via Pathway/LLM
    return split_sentences(text)
