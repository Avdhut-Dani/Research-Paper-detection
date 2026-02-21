def generate_review(analysis_data, integrity_breakdown, text):
    """
    Synthesizes all analysis metrics into a qualitative 'Peer Review'.
    Categories: Strengths, Weaknesses, Critical Red Flags.
    """
    review = {
        "strengths": [],
        "weaknesses": [],
        "red_flags": []
    }
    
    rigor = analysis_data.get("rigor", {})
    novelty = analysis_data.get("novelty", {})
    
    # --- STRENGTHS ---
    if novelty.get("has_contribution_statement"):
        review["strengths"].append({"text": "Clearly defined contribution statement found.", "source": "Novelty Analysis"})
    if novelty.get("is_novelty_specific"):
        review["strengths"].append({"text": "Novelty claims are technically specific (not just generic boilerplate).", "source": "Semantic Specificity Engine"})
    if novelty.get("has_scientific_gap"):
        review["strengths"].append({"text": "Strong problem motivation; correctly identifies gaps in existing literature.", "source": "Scientific Gap Detector"})
        
    if rigor.get("has_ablation"):
        review["strengths"].append({"text": "Includes ablation studies to verify component importance.", "source": "Methodological Rigor Analysis"})
    if rigor.get("has_baselines"):
        review["strengths"].append({"text": "Compared against state-of-the-art baselines.", "source": "Methodological Rigor Analysis"})
    if rigor.get("has_statistical_validation"):
        review["strengths"].append({"text": "Utilizes statistical validation (e.g., significance testing or variance reporting).", "source": "Methodological Rigor Analysis"})
    if rigor.get("has_reproducibility"):
        review["strengths"].append({"text": "Reproducibility: Detected mentions of code, datasets, or training hyperparameters.", "source": "Reproducibility Audit"})
    if rigor.get("has_methodological_depth"):
        review["strengths"].append({"text": "Methodological Depth: Found formalized mathematical proofs or derivations.", "source": "Methodological Rigor Analysis"})
    
    # --- WEAKNESSES ---
    if not rigor.get("has_ablation"):
        review["weaknesses"].append({"text": "Lacks an explicit ablation study. It is difficult to assess the individual impact of proposed components.", "source": "Methodological Rigor Analysis"})
    if not rigor.get("has_baselines"):
        review["weaknesses"].append({"text": "Weak baseline comparison detected. Results might not be competitive with current state-of-the-art.", "source": "Methodological Rigor Analysis"})
    if not rigor.get("has_statistical_validation"):
        review["weaknesses"].append({"text": "No clear statistical significance testing or variance reports found. Performance gains might be marginal or due to chance.", "source": "Methodological Rigor Analysis"})
    
    # Unpublished/Pre-submission specific weaknesses
    if not rigor.get("has_reproducibility"):
        review["weaknesses"].append({"text": "Pre-submission Warning: No GitHub link or reproducibility section found. Highly recommended for top-tier acceptance.", "source": "Reproducibility Audit"})
    if not novelty.get("is_novelty_specific"):
        review["weaknesses"].append({"text": "Contribution specificity is low. Consider detailing the exact architectural or algorithmic shift.", "source": "Semantic Specificity Engine"})
    if not novelty.get("has_scientific_gap"):
         review["weaknesses"].append({"text": "Problem motivation is weak. The 'Why' behind this research gap is not clearly articulated.", "source": "Scientific Gap Detector"})

    # Structure checks
    critical_sections = ["limitations", "conclusion", "future work", "related work"]
    for section in critical_sections:
        if section not in text.lower():
            review["weaknesses"].append({"text": f"Structure Check: Potential missing or poorly labeled '{section.capitalize()}' section.", "source": "Document Topology Engine"})
    
    # --- CRITICAL RED FLAGS ---
    if integrity_breakdown.get("false_citations", 0) > 10: 
        review["red_flags"].append({"text": "CRITICAL: High volume of contextual citation mismatches. This often correlates with LLM-hallucination or inaccurate literature review.", "source": "RAG-based Citation Verifier"})
    
    if integrity_breakdown.get("self_citation", 0) > 20:
        review["red_flags"].append({"text": "Heavy Self-Citation index. This can be flagged as 'Citation Gaming' by some reviewers.", "source": "Author Affinity Analysis"})
        
    if integrity_breakdown.get("outdated_datasets", 0) > 0:
        review["red_flags"].append({"text": "Usage of outdated/superseded benchmarks detected. Reviewers may question the relevance of performance gains on modern data.", "source": "Market Relevance/Dataset KB"})

    return review
