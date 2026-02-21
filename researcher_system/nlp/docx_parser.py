import docx

def extract_text_from_docx(path):
    """
    Extracts text from a .docx file and splits it into body and (heuristic) references.
    """
    doc = docx.Document(path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    
    combined_text = "\n".join(full_text)
    
    # Simple heuristic to split References
    # Research papers usually have a "References" or "Bibliography" header
    ref_header_pos = -1
    markers = ["REFERENCES", "References", "BIBLIOGRAPHY", "Bibliography"]
    
    for marker in markers:
        pos = combined_text.rfind(marker) # Usually at the end
        if pos > len(combined_text) * 0.7: # Heuristic: references are in the last 30%
            ref_header_pos = pos
            break
            
    if ref_header_pos != -1:
        body = combined_text[:ref_header_pos]
        references = combined_text[ref_header_pos:]
    else:
        body = combined_text
        references = ""
        
    return {
        "body": body,
        "references": references,
        "full_text": combined_text
    }
