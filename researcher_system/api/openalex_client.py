import requests
import json
import urllib.parse
import re

OPENALEX_BASE_URL = "https://api.openalex.org"

def normalize_doi(doi_str):
    """Extracts clean DOI from a URL or raw string."""
    if not doi_str:
        return None
    match = re.search(r'(10\.\d{4,9}/[-._;()/:A-Z0-9]+)', str(doi_str), re.I)
    return match.group(1).lower() if match else None

def fetch_paper_by_doi(doi):
    """
    Fetches OpenAlex data for a given DOI.
    Returns a dict with relevant metadata or None if not found.
    """
    clean_doi = normalize_doi(doi)
    if not clean_doi:
        return None
    
    url = f"{OPENALEX_BASE_URL}/works/https://doi.org/{clean_doi}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return _parse_openalex_response(response.json())
        return None
    except requests.RequestException:
        return None

def fetch_paper_by_title(title):
    """
    Fetches OpenAlex data for a given title using search.
    """
    encoded_title = urllib.parse.quote(title)
    url = f"{OPENALEX_BASE_URL}/works?filter=title.search:{encoded_title}&per-page=1"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                return _parse_openalex_response(data["results"][0])
        return None
    except requests.RequestException:
        return None
        
def _parse_openalex_response(data):
    """
    Extracts total citations, referenced DOIs, and author IDs.
    """
    authors = []
    for authorship in data.get("authorships", []):
        author = authorship.get("author", {})
        if author:
            authors.append({
                "id": author.get("id"),
                "display_name": author.get("display_name")
            })
            
    # OpenAlex returns referenced_works as OpenAlex IDs usually: "https://openalex.org/W12345"
    referenced_works = data.get("referenced_works", [])
    
    # We might want to resolve OpenAlex IDs to DOIs, or just use OpenAlex IDs directly.
    # The requirement specifically mentions DOIs, but OpenAlex provides 'referenced_works' as W-IDs by default.
    # We can fetch minimal metadata for these if necessary later.
    
    return {
        "id": data.get("id"),
        "doi": normalize_doi(data.get("doi")),
        "title": data.get("title"),
        "publication_year": data.get("publication_year"),
        "type": data.get("type"),
        "is_oa": data.get("open_access", {}).get("is_oa", False) if isinstance(data.get("open_access"), dict) else False,
        "cited_by_count": data.get("cited_by_count", 0),
        "referenced_works_ids": referenced_works,  # OpenAlex IDs
        "authors": authors
    }

def fetch_authors_for_works(work_ids):
    """
    Given a list of OpenAlex work IDs, fetches their authors in batch.
    """
    if not work_ids:
        return {}
        
    results = {}
    # Batch query pattern: https://api.openalex.org/works?filter=openalex:W1|W2|W3
    # OpenAlex limits to 50 filters per query. We'll chunk them.
    chunk_size = 50
    for i in range(0, len(work_ids), chunk_size):
        chunk = work_ids[i:i+chunk_size]
        # remove prefix if present
        cleaned_chunk = [w.split("/")[-1] for w in chunk]
        filter_str = "|".join(cleaned_chunk)
        url = f"{OPENALEX_BASE_URL}/works?filter=openalex:{filter_str}&per-page={chunk_size}"
        
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                for work in data.get("results", []):
                    work_id = work.get("id")
                    authors = []
                    for auth in work.get("authorships", []):
                        a = auth.get("author", {})
                        if a and a.get("id"):
                            authors.append(a.get("id"))
                    results[work_id] = authors
        except requests.RequestException:
            pass
            
    return results

def fetch_abstracts_for_works(work_ids):
    """
    Given a list of OpenAlex work IDs, fetches their abstracts in batch.
    Reconstructs the abstract string from the abstract_inverted_index.
    """
    if not work_ids:
        return {}
        
    results = {}
    chunk_size = 50
    for i in range(0, len(work_ids), chunk_size):
        chunk = work_ids[i:i+chunk_size]
        cleaned_chunk = [w.split("/")[-1] for w in chunk]
        filter_str = "|".join(cleaned_chunk)
        url = f"{OPENALEX_BASE_URL}/works?filter=openalex:{filter_str}&per-page={chunk_size}"
        
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                for work in data.get("results", []):
                    work_id = work.get("id")
                    inv_index = work.get("abstract_inverted_index")
                    
                    if inv_index:
                        # Reconstruct abstract
                        word_index = []
                        for word, positions in inv_index.items():
                            for pos in positions:
                                word_index.append((pos, word))
                        # Sort by position
                        word_index.sort(key=lambda x: x[0])
                        abstract = " ".join([w[1] for w in word_index])
                        results[work_id] = abstract
                    else:
                        results[work_id] = ""
        except requests.RequestException:
            pass
            
    return results
