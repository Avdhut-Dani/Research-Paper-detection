from researcher_system.api.openalex_client import fetch_authors_for_works

def compute_self_citations(target_author_ids, referenced_work_ids):
    """
    Computes self citations by checking the intersection of author IDs
    between the target paper and its referenced works.
    
    Args:
        target_author_ids (list): List of OpenAlex author IDs for the target paper.
        referenced_work_ids (list): List of OpenAlex work IDs cited by the target paper.
        
    Returns:
        dict: {
            "total_references": int,
            "self_citation_count": int,
            "self_citation_ratio": float,
            "self_cited_works": list of work IDs
        }
    """
    if not target_author_ids or not referenced_work_ids:
        return {
            "total_references": len(referenced_work_ids) if referenced_work_ids else 0,
            "self_citation_count": 0,
            "self_citation_ratio": 0.0,
            "self_cited_works": []
        }
        
    target_authors_set = set(target_author_ids)
    
    # Fetch authors for all referenced works
    works_authors_map = fetch_authors_for_works(referenced_work_ids)
    
    self_cited_works = []
    
    for work_id, author_ids in works_authors_map.items():
        cited_authors_set = set(author_ids)
        if target_authors_set.intersection(cited_authors_set):
            self_cited_works.append(work_id)
            
    total_refs = len(referenced_work_ids)
    self_citations = len(self_cited_works)
    
    return {
        "total_references": total_refs,
        "self_citation_count": self_citations,
        "self_citation_ratio": self_citations / total_refs if total_refs > 0 else 0.0,
        "self_cited_works": self_cited_works
    }

def extract_authors_heuristic(body_text):
    """
    Attempts to extract author last names from the first few lines of the paper.
    """
    lines = body_text.split('\n')
    author_last_names = set()
    
    # Authors are usually found between lines 1 to 20
    # Look for capitalized words that might be names, often comma-separated or with symbols
    import re
    for line in lines[1:20]:
        line = line.strip()
        # Skip common non-author lines
        if not line or len(line) < 3 or line.lower().startswith('abstract') or '@' in line or 'university' in line.lower() or 'department' in line.lower():
            continue
            
        # Very basic split by commas or 'and'
        potential_names = re.split(r',|\band\b', line)
        for name in potential_names:
            name = name.strip()
            # Remove academic titles or weird characters
            name = re.sub(r'[^a-zA-Z\s\-]', '', name)
            words = name.split()
            if len(words) >= 2 and len(words) <= 4: # e.g. "Arjun Mehta"
                # Assume the last word is the last name
                last_name = words[-1]
                if len(last_name) > 2 and last_name[0].isupper():
                    author_last_names.add(last_name)
                    
    return list(author_last_names)

def fallback_self_citation_ratio(bib_map, body_text):
    """
    Heuristic method for string-matching self-citations when API data is unavailable.
    """
    authors = extract_authors_heuristic(body_text)
    if not authors or not bib_map:
        return 0.0, 0
        
    count = 0
    total = len(bib_map)
    if not isinstance(bib_map, dict):
        return 0.0, 0
        
    for cit_marker, text in bib_map.items():
        text_lower = str(text).lower()
        # If any extracted author's last name appears in the citation string
        if any(a.lower() in text_lower for a in authors):
            count += 1
            
    ratio = count / total if total > 0 else 0.0
    return ratio, count
