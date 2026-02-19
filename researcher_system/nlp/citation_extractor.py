import re

def extract_citations(text):
    citations = []
    
    # Pattern 1: (Author, Year) or (Author et al., Year)
    # e.g., (Smith, 2020), (Doe et al., 2019)
    pattern_auth_year = r'\([A-Z][a-zA-Z\s]+(?:et al\.)?,\s*\d{4}\)'
    citations.extend(re.findall(pattern_auth_year, text))

    # Pattern 2: Bracket numbers [1], [1, 2], [1-3]
    # e.g., [1], [5, 10], [1-5]
    pattern_brackets = r'\[\d+(?:,\s*\d+|-?\d+)*\]'
    citations.extend(re.findall(pattern_brackets, text))
    
    return list(set(citations))  # Deduplicate
