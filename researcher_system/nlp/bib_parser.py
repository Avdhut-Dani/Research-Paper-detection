import re

def parse_bibliography(text):
    """
    Identifies the References section and maps citation IDs to full text.
    Returns a dictionary of {id: full_text}.
    """
    # Look for References section
    ref_matches = list(re.finditer(r'(?i)\n(?:References|Bibliography)\n', text))
    if not ref_matches:
        # Fallback to searching for the start of the list if no header found
        ref_start = text.rfind('[1]')
        if ref_start == -1:
            return {}
    else:
        # We assume the last occurrence is the actual bibliography section
        ref_start = ref_matches[-1].end()

    ref_section = text[ref_start:]
    
    # Extract numerical bracket citations [1] ...
    # This regex looks for [N] followed by text until the next [N+1] or end of section
    entries = {}
    pattern = r'\[(\d+)\]\s+(.*?)(?=\s*\[\d+\]|$)'
    matches = re.findall(pattern, ref_section, re.DOTALL)
    
    for citation_id, content in matches:
        clean_content = re.sub(r'\s+', ' ', content).strip()
        entries[f"[{citation_id}]"] = clean_content
        
    return entries
