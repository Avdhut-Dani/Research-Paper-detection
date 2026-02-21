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

def fallback_self_citation_ratio(citations, authors=["author"]):
    """
    Legacy method for string-matching self-citations when API data is unavailable.
    """
    count = 0
    for c in citations:
        if any(bool(a) and str(a).lower() in str(c).lower() for a in authors):
            count += 1
    return count / len(citations) if citations else 0

