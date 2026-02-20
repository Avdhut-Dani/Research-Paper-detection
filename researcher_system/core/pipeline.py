from researcher_system.nlp.pdf_parser import extract_text
from researcher_system.core.pathway_pipeline import run_pathway_analysis
from researcher_system.nlp.bib_parser import parse_bibliography
from researcher_system.nlp.citation_extractor import extract_citations
from researcher_system.analysis.semantic_relevance import relevance
from researcher_system.models.vague_detector import is_vague
from researcher_system.analysis.self_citation_analysis import self_citation_ratio
from researcher_system.analysis.integrity_scoring import score

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

    self_ratio = self_citation_ratio(citation_mentions)
    integrity = score(avg_rel, self_ratio, len(refined_vague))

    # Map each mention to its bibliography entry for the UI list
    display_citations = []
    for cit in citation_mentions:
        full = bib_map.get(cit, cit)
        if full not in display_citations:
            display_citations.append(full)

    return {
        "claims": len(refined_solid),
        "vague_claims": len(refined_vague),
        "citations": len(bib_map) if bib_map else len(citation_mentions),
        "integrity_score": integrity,
        "avg_relevance": avg_rel,
        "self_citation_ratio": self_ratio,
        "claims_list": [c['text'] for c in refined_solid] + [c['text'] for c in refined_vague],
        "citation_list": display_citations,
        "solid_claims": refined_solid,
        "vague_claims_list": refined_vague,
        "detailed_citations": detailed_citations,
        "bibliography": bib_map
    }
