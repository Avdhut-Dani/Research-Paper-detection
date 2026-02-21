import re
import nltk
from nltk.tokenize import sent_tokenize

# Ensure punkt is available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)

def extract_citations(text):
    """
    Extracts mere citation markers (kept for backward compatibility).
    """
    citations = []
    
    pattern_auth_year = r'\([A-Z][a-zA-Z\s]+(?:et al\.)?,\s*\d{4}\)'
    citations.extend(re.findall(pattern_auth_year, text))

    pattern_brackets = r'\[\d+(?:,\s*\d+|-?\d+)*\]'
    citations.extend(re.findall(pattern_brackets, text))
    
    return list(set(citations))

def extract_citation_contexts(text):
    """
    Extracts citation markers along with their surrounding sentence context.
    Returns:
        dict: { "citation_marker": ["sentence 1 context", "sentence 2 context"] }
    """
    sentences = sent_tokenize(text)
    
    pattern_auth_year = re.compile(r'\([A-Z][a-zA-Z\s]+(?:et al\.)?,\s*\d{4}\)')
    pattern_brackets = re.compile(r'\[\d+(?:,\s*\d+|-?\d+)*\]')
    
    contexts = {}
    
    for sent in sentences:
        # Find matches in the current sentence
        auth_year_matches = pattern_auth_year.findall(sent)
        bracket_matches = pattern_brackets.findall(sent)
        
        all_matches = set(auth_year_matches + bracket_matches)
        
        for match in all_matches:
            if match not in contexts:
                contexts[match] = []
            contexts[match].append(sent.strip())
            
    return contexts
