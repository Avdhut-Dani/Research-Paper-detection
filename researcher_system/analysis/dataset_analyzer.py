import json
import re
import os
from datetime import datetime

# Load Dataset KB path
KB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core', 'datasets_kb.json')

def get_datasets_kb():
    try:
        with open(KB_PATH, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def extract_datasets_from_text(text):
    """
    Extracts dataset names from text using known KB matching + dynamic regex for missing ones.
    Returns a list of unique dataset names found.
    """
    found_datasets = []
    kb = get_datasets_kb()
    if not isinstance(kb, dict):
        return []
    
    # 1. Match Known KB Datasets
    kb_names = sorted(list(kb.keys()), key=len, reverse=True)
    for name in kb_names:
        escaped_name = re.escape(name)
        pattern = rf'\b{escaped_name}\b'
        if not name[-1].isalnum():
            pattern = rf'{escaped_name}(?!\w)'
            
        if re.search(pattern, text, re.IGNORECASE):
            found_datasets.append(name)
            # Remove matched text so substrings aren't double counted
            text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)
            
    # 2. Dynamic Regex Extraction (e.g., "CapitalWords [12]")
    dynamic_pattern = r'\b([A-Z][A-Za-z0-9+-]+(?:\s+[A-Z][A-Za-z0-9+-]+)*)\s*(?:\([A-Za-z0-9+-]+\))?\s*\[\d+(?:,\s*\d+)*\]'
    dynamic_matches = re.findall(dynamic_pattern, text)
    stopwords = {"Figure", "Table", "Section", "In", "The", "We", "A", "This", "Eq", "Equation", "Ref", "Reference", "Let"}
    for m in dynamic_matches:
        clean_m = m.strip()
        if len(clean_m) > 2 and clean_m not in stopwords and clean_m not in found_datasets:
            found_datasets.append(clean_m)
            
    return list(set(found_datasets))

def analyze_dataset_usage(datasets_found, current_year=None, age_threshold=8):
    """
    Analyzes the datasets used in a paper and flags any that are outdated.
    Also provides a market comparison based on the identified domain.
    """
    if not current_year:
        current_year = datetime.now().year
        
    warnings = []
    kb = get_datasets_kb()
    
    # Identify domains of extracted datasets
    identified_domains = {}
    for ds in datasets_found:
        info = kb.get(ds)
        if info:
            domain = info.get("domain")
            if domain:
                identified_domains[domain] = identified_domains.get(domain, 0) + 1
                
        if not info:
            continue
            
        ds_year = info.get("year", current_year)
        try:
            age = int(current_year) - int(ds_year)
        except (ValueError, TypeError):
            age = 0
        superseded_by = info.get("superseded_by", [])
        
        is_outdated = False
        reason = ""
        
        if age >= age_threshold and superseded_by:
            is_outdated = True
            reason = f"{ds} is {age} years old. Newer alternatives exist: {', '.join(superseded_by)}."
        elif superseded_by and not any(newer in datasets_found for newer in superseded_by):
            is_outdated = True
            reason = f"{ds} has modern alternatives ({', '.join(superseded_by)}) which were not utilized."
            
        if is_outdated:
            warnings.append({
                "dataset": ds,
                "reason": reason
            })
            
    # Derive market comparison based on primary domain (if any)
    market_comparison = None
    if identified_domains:
        primary_domain = max(identified_domains, key=lambda k: identified_domains[k])
        # Get all datasets in KB for this domain
        domain_datasets = [(k, v) for k, v in kb.items() if isinstance(v, dict) and v.get("domain") == primary_domain]
        domain_datasets.sort(key=lambda x: int(x[1].get("year", 0)), reverse=True) # Sort newest first
        
        latest_datasets = [f"{k} ({v.get('year')})" for k, v in domain_datasets[:5]]
        used_in_domain = [ds for ds in datasets_found if kb.get(ds, {}).get("domain") == primary_domain]
        missed_opportunities = [k for k, v in domain_datasets[:3] if k not in datasets_found]
        
        analysis_text = f"The author primarily evaluated on {primary_domain} datasets."
        if missed_opportunities:
            analysis_text += f" They missed incorporating the latest leading datasets in the market such as {', '.join(missed_opportunities)}."
        else:
            analysis_text += " They successfully incorporated the latest available benchmarks in this field."
            
        market_comparison = {
            "domain": primary_domain,
            "latest_available": latest_datasets,
            "missed": missed_opportunities,
            "analysis": analysis_text
        }
            
    return {
        "datasets_found": datasets_found,
        "outdated_warnings": warnings,
        "market_comparison": market_comparison
    }
