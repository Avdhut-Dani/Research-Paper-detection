import pathway as pw
from researcher_system.nlp.claim_segmenter import split_sentences
from researcher_system.models.llm_classifier import get_detailed_classification

class SentenceSchema(pw.Schema):
    sentence: str
    label: str
    score: float

def _is_claim_label(label: str) -> bool:
    return label in ["solid_claim", "vague_claim"]

def is_claim_like(sentence: str) -> bool:
    """Heuristic to reduce LLM load by filtering out noise."""
    lower_s = sentence.lower().strip()
    
    # Negative filters: common research paper filler/structure
    skip_keywords = ["figure", "table", "section", "chapter", "below", "following", "above", "et al.", "i.e.", "e.g."]
    if any(k in lower_s for k in skip_keywords) and len(lower_s) < 100:
        return False
        
    # Positive filters: Indicators of a research claim
    claim_indicators = ["propose", "method", "achieve", "result", "finding", "conclude", "demonstrate", "evidence", "significant", "superior", "improve"]
    if any(k in lower_s for k in claim_indicators):
        return True
        
    # Basic structural check: Must have "we" or "our" or be a descriptive sentence
    if "we " in lower_s or "our " in lower_s:
        return True
        
    return False

def run_pathway_analysis(text):
    """
    Uses Pathway to process the provided text and extract classified claims.
    """
    from researcher_system.models.llm_classifier import get_classifier
    
    sentences = [s for s in split_sentences(text) if len(s) > 20]
    print(f"[DEBUG] Total sentences extracted: {len(sentences)}")
    
    # Heuristic filter to reduce LLM calls
    candidate_sentences = [s for s in sentences if is_claim_like(s)]
    print(f"[DEBUG] Claim candidates after heuristic: {len(candidate_sentences)}")

    if not candidate_sentences:
        return []

    # Batch classify using GPU optimization
    clf = get_classifier()
    classifications = clf.classify_batch(candidate_sentences)
    
    # Prepare data for Pathway: combine sentence with its classification
    data = []
    for s, c in zip(candidate_sentences, classifications):
        data.append((s, c['label'], c['score']))

    # Pathway table creation with pre-classified data
    t = pw.debug.table_from_rows(SentenceSchema, data)
    
    # Filter for solid or vague claims in Pathway
    t = t.filter(pw.apply(_is_claim_label, t.label))
    
    # Collect results
    pointers, columns = pw.debug.table_to_dicts(t)
    sentence_col = columns.get('sentence', {})
    label_col = columns.get('label', {})
    score_col = columns.get('score', {})
    
    results = []
    for ptr in pointers:
        results.append({
            "sentence": sentence_col[ptr],
            "label": label_col[ptr],
            "score": score_col[ptr]
        })
    print(f"[DEBUG] Found {len(results)} claims via LLM batching.")
    return results
