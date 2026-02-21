from researcher_system.nlp.pdf_parser import extract_text
from researcher_system.core.pathway_pipeline import run_pathway_analysis
from researcher_system.nlp.bib_parser import parse_bibliography
from researcher_system.nlp.citation_extractor import extract_citations
from researcher_system.analysis.semantic_relevance import relevance
from researcher_system.models.vague_detector import is_vague
from researcher_system.models.vague_detector import is_vague
from researcher_system.analysis.self_citation_analysis import compute_self_citations, fallback_self_citation_ratio
from researcher_system.analysis.integrity_scoring import score
from researcher_system.api.openalex_client import fetch_paper_by_title, fetch_paper_by_doi, fetch_abstracts_for_works
from researcher_system.analysis.false_citation_detector import detect_false_citations
from researcher_system.analysis.dataset_analyzer import extract_datasets_from_text, analyze_dataset_usage

def extract_title_heuristic(text):
    lines = text.split('\n')
    for line in lines[:10]:
        line = line.strip()
        if len(line) > 10 and not line.lower().startswith('arxiv'):
            return line
    return "Unknown Title"

def fuzzy_match_titles(t1, t2):
    if not t1 or not t2: return False
    # Very basic inclusion match for safety
    import re
    t1_clean = re.sub(r'[^a-zA-Z0-9]', '', t1.lower())
    t2_clean = re.sub(r'[^a-zA-Z0-9]', '', t2.lower())
    return t1_clean in t2_clean or t2_clean in t1_clean

def run_pipeline(path=None, doi=None, filename=None):
    analysis_mode = "UNKNOWN"
    paper_metadata = None
    body_text = ""
    ref_text = ""
    bib_map = {}
    citation_mentions = []
    
    # CASE 3: DOI ONLY
    if doi and not path:
        analysis_mode = "DOI_ONLY"
        paper_metadata = fetch_paper_by_doi(doi)
        
    # CASE 1 & 2: PDF PROVIDED
    elif path:
        parsed_content = extract_text(path)
        body_text = parsed_content["body"]
        ref_text = parsed_content["references"]
        bib_map = parse_bibliography(ref_text if ref_text else body_text)
        citation_mentions = extract_citations(body_text)
        
        # User requested: Use the uploaded filename as the intended paper title (stripping extension)
        if filename:
            import os
            pdf_title = os.path.splitext(filename)[0].replace("_", " ")
        else:
            pdf_title = extract_title_heuristic(body_text)
        
        if doi:
            # CASE 1: BOTH PROVIDED
            # Trust the user's DOI if it resolves. Title heuristic is unreliable
            # (published PDFs often start with journal name/headers, not the title).
            temp_metadata = fetch_paper_by_doi(doi)
            if temp_metadata:
                if fuzzy_match_titles(pdf_title, temp_metadata.get("title", "")):
                    analysis_mode = "MATCHED_HYBRID"
                else:
                    analysis_mode = "MATCHED_HYBRID_WARN"  # titles differ, but user provided DOI
                    # Title mismatch: user requested to prioritize DOI and ignore PDF parsing. 
                    body_text = ""
                    ref_text = ""
                    bib_map = {}
                    citation_mentions = []
                paper_metadata = temp_metadata
            else:
                # DOI resolved to nothing → fall back to PDF only
                analysis_mode = "PDF_ONLY"
                paper_metadata = None
        else:
            # CASE 2: PDF ONLY
            analysis_mode = "PDF_ONLY"
            paper_metadata = None
            
    # IF DOI ONLY but invalid DOI
    if analysis_mode == "DOI_ONLY" and not paper_metadata:
        return {"error": "Could not find metadata for provided DOI."}

    # Initialize default values
    avg_rel = 0.0
    self_ratio = 0.0
    self_cit_data = {"self_citation_count": 0, "total_references": 0}
    false_citations = []
    refined_solid = []
    refined_vague = []
    display_citations = []
    detailed_citations = []
    dataset_names = []
    outdated_datasets = []
    dataset_analysis = {}

    # 3. Run Pathway/LLM analysis on the BODY only (If PDF is available and titles match)
    raw_claims = []
    if analysis_mode in ["MATCHED_HYBRID", "PDF_ONLY"]:
        raw_claims = run_pathway_analysis(body_text)
    
    solid_claims = []
    vague_claims = []

    # Map each mention to its bibliography entry
    for cit in citation_mentions:
        full_text = bib_map.get(cit, "Full citation text not found in bibliography.")
        detailed_citations.append({
            "id": cit,
            "full_text": full_text
        })

    for c in raw_claims:
        sentence = c['sentence']
        label = c['label']
        score_val = c['score']
        
        # Stricter thresholds for noise reduction
        if score_val < 0.4:
            continue
            
        # RAG-base Verification logic
        verified = True
        verification_note = "No specific citation linked in sentence."
        
        import re
        mentions = re.findall(r"\[(\d+)\]", sentence)
        if mentions:
            for m in mentions:
                cit_id = f"[{m}]"
                if cit_id in bib_map:
                    rel_val = relevance(sentence, bib_map[cit_id])
                    if rel_val < 0.3:
                        verified = False
                        verification_note = f"Possible Misalignment with {cit_id} (Relevance: {rel_val:.2f})"
                        break
                    else:
                        verification_note = f"Verified with {cit_id} (Relevance: {rel_val:.2f})"

        claim_data = {
            "text": sentence,
            "score": score_val,
            "verified": verified,
            "verification_note": verification_note
        }

        # Final classification refinement
        # If it has vague words, it's a vague claim regardless of LLM label peak
        if is_vague(sentence) or score_val < 0.65:
            vague_claims.append(claim_data)
        elif label == "solid_claim":
            solid_claims.append(claim_data)
        else:
            # If LLM said "vague_claim" but we didn't hit vague words and score is high (>=0.65)?
            # Keep as vague to be safe unless it's a very solid finding.
            vague_claims.append(claim_data)

    # Calculate overall metrics
    all_rel_scores = []
    if citation_mentions and solid_claims:
        for sc in solid_claims:
             all_rel_scores.append(relevance(sc['text'], citation_mentions[0]))
    
    avg_rel = sum(all_rel_scores) / len(all_rel_scores) if all_rel_scores else 0
    # 1. Extract years from bibliography
    bib_years = {}
    import re
    for ref_id, text in bib_map.items():
        year_match = re.search(r'\b(19|20)\d{2}\b', text)
        if year_match:
            bib_years[ref_id] = int(year_match.group(0))

    from researcher_system.models.llm_classifier import get_decay_analysis
    current_year = 2026
    
    def check_freshness(claim_text):
        decay_type, reason, moving_vars, stress_test, consensus = get_decay_analysis(claim_text)
        mentions = extract_citations(claim_text)
        cited_years = [bib_years[m] for m in mentions if m in bib_years]
        
        # Determine threshold based on architecture (half-lives)
        threshold_map = {
            "FAST": 1.5,
            "MEDIUM": 4.0,
            "SLOW": 15.0,
            "TIMELESS": 100.0
        }
        half_life = float(threshold_map.get(decay_type, 5.0))
        
        is_fresh = True
        freshness_score = 100.0
        
        if cited_years:
            avg_year = float(sum(cited_years)) / len(cited_years)
            age = float(current_year - avg_year)
            
            # Accelerate decay if moving variables are present
            decay_accelerator = 1.0 + (0.2 * len(moving_vars))
            
            # Freshness score decays as age approaches/exceeds half-life
            freshness_score = max(0.0, min(100.0, 100.0 * (1.0 - (age / (half_life * 2.5 * (1/decay_accelerator))))))
            
            if age > (half_life / decay_accelerator):
                is_fresh = False
        
        return {
            "is_outdated": not is_fresh,
            "decay_type": decay_type,
            "reason": reason,
            "moving_variables": moving_vars,
            "stress_test": stress_test,
            "consensus": consensus,
            "freshness_score": round(float(freshness_score), 1),
            "cited_years": cited_years,
            "half_life": half_life
        }

    # Process Solid Claims
    refined_solid = []
    for sc in solid_claims:
        fresh_data = check_freshness(sc['text'])
        sc.update(fresh_data)
        refined_solid.append(sc)

    # Process Vague Claims
    refined_vague = []
    for vc in vague_claims:
        fresh_data = check_freshness(vc['text'])
        vc.update(fresh_data)
        refined_vague.append(vc)

    # Map each mention to its bibliography entry for the UI list
    display_citations = []
    for cit in citation_mentions:
        full = bib_map.get(cit, cit)
        if full not in display_citations:
            display_citations.append(full)

    # --- NEW: Advanced Metrics Integration ---
    # 1. OpenAlex & Self-Citations
    
    # We already have paper_metadata if MATCHED_HYBRID or DOI_ONLY
    if paper_metadata:
        target_author_ids = [a['id'] for a in paper_metadata.get('authors', [])]
        referenced_work_ids = paper_metadata.get('referenced_works_ids', [])
        
        self_cit_data = compute_self_citations(target_author_ids, referenced_work_ids)
        self_ratio = self_cit_data.get('self_citation_ratio', 0.0)
        
        # 2. False Citation Detection (Only if we have matched PDF text to compare)
        if analysis_mode in ["MATCHED_HYBRID"]:
            from researcher_system.nlp.citation_extractor import extract_citation_contexts
            citation_contexts = extract_citation_contexts(body_text)
            cited_abstracts_map = fetch_abstracts_for_works(referenced_work_ids)
            
            mapped_abstracts = {}
            for i, cit_marker in enumerate(bib_map.keys()):
                if i < len(referenced_work_ids):
                    work_id = referenced_work_ids[i]
                    mapped_abstracts[cit_marker] = cited_abstracts_map.get(work_id, "")
                    
            false_citations = detect_false_citations(citation_contexts, mapped_abstracts)
    elif analysis_mode == "PDF_ONLY":
        # PDF_ONLY Case Heuristics
        self_ratio, self_count = fallback_self_citation_ratio(bib_map, body_text)
        self_cit_data = {"self_citation_count": self_count, "total_references": len(citation_mentions)}
        
        # Heuristic False Citation: Correlate claim immediately against reference string
        if citation_mentions:
            from researcher_system.nlp.citation_extractor import extract_citation_contexts
            citation_contexts = extract_citation_contexts(body_text)
            # Map citation to raw bibliography text instead of abstract
            false_citations = detect_false_citations(citation_contexts, bib_map)

    # 3. Dataset Outdated Analysis (Requires PDF Text)
    if analysis_mode in ["MATCHED_HYBRID", "PDF_ONLY"]:
        dataset_names = extract_datasets_from_text(body_text)
        dataset_analysis = analyze_dataset_usage(dataset_names, current_year=current_year)
        outdated_datasets = dataset_analysis.get('outdated_warnings', [])
    
    # Calculate robust integrity score dynamically based on available analysis mode data
    integrity_breakdown = {}
    if analysis_mode in ["DOI_ONLY", "MATCHED_HYBRID_WARN"]:
        # Without full PDF text, we cannot genuinely assess paper integrity
        integrity = None
    else:
        # Base score 100
        integrity = 100.0
        
        # 1. Self-citation penalty (Heavy: up to 30 points)
        self_cit_penalty = min(30.0, self_ratio * 30.0)
        integrity -= self_cit_penalty
        integrity_breakdown["self_citation"] = round(self_cit_penalty, 2)
        
        # 2. Vague claims penalty (Proportional: up to 25 points)
        # Instead of fixed per-claim, we look at the ratio of vague vs solid
        total_claims_found = len(refined_solid) + len(refined_vague)
        if total_claims_found > 0:
            vague_ratio = len(refined_vague) / total_claims_found
            vague_penalty = min(25.0, vague_ratio * 35.0) # Up to 35 points penalty for 100% vague
        else:
            vague_penalty = 0.0
        integrity -= vague_penalty
        integrity_breakdown["vague_claims"] = round(vague_penalty, 2)
        
        # 3. False citation penalty (Critical: 15 points per false citation, cap at 45)
        false_cit_penalty = min(45.0, len(false_citations) * 15.0)
        integrity -= false_cit_penalty
        integrity_breakdown["false_citations"] = round(false_cit_penalty, 2)
        
        # 4. Outdated dataset penalty (5 points per outdated dataset, cap at 15)
        outdated_penalty = min(15.0, len(outdated_datasets) * 5.0)
        integrity -= outdated_penalty
        integrity_breakdown["outdated_datasets"] = round(outdated_penalty, 2)
        
        # 5. Semantic Relevance Penalty (Up to 20 points)
        if len(citation_mentions) > 0:
            rel_penalty = (1.0 - max(0.0, avg_rel)) * 20.0
            integrity -= rel_penalty
            integrity_breakdown["low_relevance"] = round(rel_penalty, 2)
        else:
            integrity_breakdown["low_relevance"] = 0.0
            
        # 6. Freshness Bonus (Reward papers with highly fresh solid claims, cap at 10)
        fresh_bonus = min(10.0, sum(1 for c in refined_solid if c.get('freshness_score', 0) >= 80) * 2.0)
        integrity += fresh_bonus
        integrity_breakdown["freshness_bonus"] = round(fresh_bonus, 2)
        
        # Clamp between 0 and 100
        integrity = max(0.0, min(100.0, integrity))

    # Use API citation count when we have metadata (more accurate than bib_map count)
    api_cited_by = paper_metadata.get("cited_by_count", None) if paper_metadata else None
    api_references_count = len(paper_metadata.get("referenced_works_ids", [])) if paper_metadata else None

    return {
        "analysis_mode": analysis_mode,
        "claims": len(refined_solid),
        "vague_claims": len(refined_vague),
        # Prefer API citation count over local bib_map count when available
        "citations": len(bib_map) if bib_map else len(citation_mentions),
        "cited_by_count": api_cited_by,           # Times this paper was cited by others
        "api_references_count": api_references_count,  # Number of references per API
        "integrity_score": integrity,
        "avg_relevance": avg_rel,
        "self_citation_ratio": self_ratio,
        "self_citation_count": self_cit_data.get("self_citation_count", 0),
        "claims_list": [c['text'] for c in refined_solid] + [c['text'] for c in refined_vague],
        "citation_list": display_citations,
        "solid_claims": refined_solid,
        "vague_claims_list": refined_vague,
        "detailed_citations": detailed_citations,
        "bibliography": bib_map,
        "false_citations": false_citations,
        "datasets_found": dataset_names,
        "outdated_datasets": outdated_datasets,
        "market_comparison": dataset_analysis.get("market_comparison"),
        "paper_metadata": paper_metadata,
        "integrity_breakdown": integrity_breakdown,
        "total_citations_count": api_references_count if (api_references_count and api_references_count > 0) else len(bib_map) if bib_map else len(citation_mentions)
    }
