from researcher_system.nlp.pdf_parser import extract_text
from researcher_system.core.pathway_pipeline import run_pathway_analysis
from researcher_system.nlp.bib_parser import parse_bibliography
from researcher_system.nlp.citation_extractor import extract_citations
from researcher_system.analysis.semantic_relevance import relevance
from researcher_system.models.vague_detector import is_vague
from researcher_system.models.vague_detector import is_vague
from researcher_system.analysis.self_citation_analysis import compute_self_citations, fallback_self_citation_ratio
from researcher_system.analysis.integrity_scoring import score
from researcher_system.api.openalex_client import fetch_paper_by_title, fetch_abstracts_for_works
from researcher_system.analysis.false_citation_detector import detect_false_citations
from researcher_system.analysis.dataset_analyzer import extract_datasets_from_text, analyze_dataset_usage

def extract_title_heuristic(text):
    lines = text.split('\n')
    for line in lines[:10]:
        line = line.strip()
        if len(line) > 10 and not line.lower().startswith('arxiv'):
            return line
    return "Unknown Title"

def run_pipeline(path):
    # 1. Extract raw text with body/references split
    parsed_content = extract_text(path)
    body_text = parsed_content["body"]
    ref_text = parsed_content["references"]

    # 2. Extract bibliography entries [id] -> full_text from the references section
    bib_map = parse_bibliography(ref_text if ref_text else body_text)

    # 3. Run Pathway/LLM analysis on the BODY only
    raw_claims = run_pathway_analysis(body_text)
    
    # 4. Extract citation mentions from the body
    citation_mentions = extract_citations(body_text)

    solid_claims = []
    vague_claims = []
    detailed_citations = []

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
    title_guess = extract_title_heuristic(body_text)
    paper_metadata = fetch_paper_by_title(title_guess)
    
    if paper_metadata:
        target_author_ids = [a['id'] for a in paper_metadata.get('authors', [])]
        referenced_work_ids = paper_metadata.get('referenced_works_ids', [])
        
        self_cit_data = compute_self_citations(target_author_ids, referenced_work_ids)
        self_ratio = self_cit_data.get('self_citation_ratio', 0.0)
        
        # 2. False Citation Detection
        from researcher_system.nlp.citation_extractor import extract_citation_contexts
        citation_contexts = extract_citation_contexts(body_text)
        cited_abstracts_map = fetch_abstracts_for_works(referenced_work_ids)
        
        # We need a mapped version where the dict key is the citation text, e.g. "[1]"
        # Since we can't easily map "[1]" to an OpenAlex ID without DOI matching in the bib map,
        # we'll approximate: we pass the retrieved abstracts and compare contexts anyway.
        # This is simplified due to citation marker vs DOI mapping complexity.
        # Let's map any abstract to any citation for testing, or rely on text matching.
        # Actually, detect_false_citations expects a mapping { marker: abstract }.
        # We will use the first N abstracts for the first N bibliography items.
        
        mapped_abstracts = {}
        for i, cit_marker in enumerate(bib_map.keys()):
            if i < len(referenced_work_ids):
                work_id = referenced_work_ids[i]
                mapped_abstracts[cit_marker] = cited_abstracts_map.get(work_id, "")
                
        false_citations = detect_false_citations(citation_contexts, mapped_abstracts)
    else:
        self_ratio = fallback_self_citation_ratio(citation_mentions)
        false_citations = []
        self_cit_data = {"self_citation_count": 0, "total_references": len(citation_mentions)}

    # 3. Dataset Outdated Analysis
    dataset_names = extract_datasets_from_text(body_text)
    dataset_analysis = analyze_dataset_usage(dataset_names, current_year=current_year)
    outdated_datasets = dataset_analysis.get('outdated_warnings', [])
    
    # Calculate integrity score with new metrics
    integrity = score(avg_rel, self_ratio, len(refined_vague))
    # Deduct points for false citations and outdated datasets
    integrity -= len(false_citations) * 5
    integrity -= len(outdated_datasets) * 5
    integrity = max(0, min(100, integrity))

    return {
        "claims": len(refined_solid),
        "vague_claims": len(refined_vague),
        "citations": len(bib_map) if bib_map else len(citation_mentions),
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
        "market_comparison": dataset_analysis.get("market_comparison")
    }
