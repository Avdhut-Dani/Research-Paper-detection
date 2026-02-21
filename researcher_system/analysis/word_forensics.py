import docx
import datetime

def analyze_word_forensics(path):
    """
    Extracts forensic metadata from a Word document.
    """
    doc = docx.Document(path)
    core_props = doc.core_properties
    
    results = {
        "metadata": {
            "creator": getattr(core_props, 'author', "Unknown") or "Unknown",
            "last_modified_by": getattr(core_props, 'last_modified_by', "Unknown") or "Unknown",
            "created": str(core_props.created) if core_props.created else "N/A",
            "modified": str(core_props.modified) if core_props.modified else "N/A",
            "revision": getattr(core_props, 'revision', 0) or 0,
            "total_editing_time": "N/A" # python-docx doesn't support ExtendedProps easily
        },
        "forensic_flags": [],
        "risk_level": "LOW"
    }
    
    # 1. Word occupancy checks
    word_count = 0
    for para in doc.paragraphs:
        word_count += len(para.text.split())

    # 2. Creator metadata checks
    ai_keywords = ["chatgpt", "openai", "claude", "bot", "assistant"]
    creator_lower = results["metadata"]["creator"].lower()
    if any(k in creator_lower for k in ai_keywords):
        results["forensic_flags"].append({
            "type": "RED_FLAG",
            "detail": f"Creator metadata contains identified AI service keyword: '{results['metadata']['creator']}'."
        })
        results["risk_level"] = "HIGH"
        
    # 3. Revision count (Unpublished research usually has high revisions)
    if results["metadata"]["revision"] < 3 and word_count > 1000:
        results["forensic_flags"].append({
            "type": "SUSPICIOUS",
            "detail": f"Low revision count ({results['metadata']['revision']}) for a document of this length. Suggests minimal iterative refinement."
        })
        if results["risk_level"] == "LOW": results["risk_level"] = "MEDIUM"

    return results
