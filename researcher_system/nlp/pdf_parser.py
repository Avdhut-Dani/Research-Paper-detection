import re
from PyPDF2 import PdfReader

def extract_text(path):
    """
    Extracts text and separates it into 'body' and 'references' sections.
    """
    reader = PdfReader(path)
    text = ""
    for p in reader.pages:
        if p.extract_text():
            text += p.extract_text() + "\n"
    
    # More aggressive search for references section
    # Look for the header and the first citation [1] close to each other
    patterns = [
        r"(?i)references\s*\n\s*\[1\]",
        r"(?i)bibliography\s*\n\s*\[1\]",
        r"(?i)references\.?\s*\[1\]", # Glued case
        r"(?i)bibliography\.?\s*\[1\]",
        r"(?i)\n\s*references\s*\n",
        r"(?i)\n\s*bibliography\s*\n",
        r"(?i)references\s*$", # End of line
        r"(?i)bibliography\s*$"
    ]
    
    split_idx = -1
    for p in patterns:
        match = list(re.finditer(p, text, re.MULTILINE))
        if match:
            # We want the last occurrence of such a header (usually)
            current_match = match[-1].start()
            if split_idx == -1 or current_match > split_idx:
                 split_idx = current_match
                 
    # Fallback: find the last substantial [1] in the document if no header
    if split_idx == -1:
        fallback = text.rfind("[1]")
        if fallback != -1 and fallback > len(text) * 0.5: # Likely bibliography
            split_idx = fallback

    if split_idx != -1:
        return {
            "body": text[:split_idx].strip(),
            "references": text[split_idx:].strip()
        }
    else:
        return {
            "body": text.strip(),
            "references": ""
        }
