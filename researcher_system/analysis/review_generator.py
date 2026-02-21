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
        review["strengths"].append("Clearly defined contribution statement found.")
    if novelty.get("is_novelty_specific"):
        review["strengths"].append("Novelty claims are technically specific (not just generic boilerplate).")
    if novelty.get("has_scientific_gap"):
        review["strengths"].append("Strong problem motivation; correctly identifies gaps in existing literature.")
        
    if rigor.get("has_ablation"):
        review["strengths"].append("Includes ablation studies to verify component importance.")
    if rigor.get("has_baselines"):
        review["strengths"].append("Compared against state-of-the-art baselines.")
    if rigor.get("has_statistical_validation"):
        review["strengths"].append("Utilizes statistical validation (e.g., significance testing or variance reporting).")
    if rigor.get("has_reproducibility"):
        review["strengths"].append("Reproducibility: Detected mentions of code, datasets, or training hyperparameters.")
    if rigor.get("has_methodological_depth"):
        review["strengths"].append("Methodological Depth: Found formalized mathematical proofs or derivations.")
    
    # --- WEAKNESSES ---
    if not rigor.get("has_ablation"):
        review["weaknesses"].append("Lacks an explicit ablation study. It is difficult to assess the individual impact of proposed components.")
    if not rigor.get("has_baselines"):
        review["weaknesses"].append("Weak baseline comparison detected. Results might not be competitive with current state-of-the-art.")
    if not rigor.get("has_statistical_validation"):
        review["weaknesses"].append("No clear statistical significance testing or variance reports found. Performance gains might be marginal or due to chance.")
    
    # Unpublished/Pre-submission specific weaknesses
    if not rigor.get("has_reproducibility"):
        review["weaknesses"].append("Pre-submission Warning: No GitHub link or reproducibility section found. Highly recommended for top-tier acceptance.")
    if not novelty.get("is_novelty_specific"):
        review["weaknesses"].append("Contribution specificity is low. Consider detailing the exact architectural or algorithmic shift.")
    if not novelty.get("has_scientific_gap"):
         review["weaknesses"].append("Problem motivation is weak. The 'Why' behind this research gap is not clearly articulated.")

    # Structure checks
    critical_sections = ["limitations", "conclusion", "future work", "related work"]
    for section in critical_sections:
        if section not in text.lower():
            review["weaknesses"].append(f"Structure Check: Potential missing or poorly labeled '{section.capitalize()}' section.")
    
    # --- CRITICAL RED FLAGS ---
    if integrity_breakdown.get("false_citations", 0) > 10: # adjusted threshold
        review["red_flags"].append(f"CRITICAL: High volume of contextual citation mismatches. This often correlates with LLM-hallucination or inaccurate literature review.")
    
    if integrity_breakdown.get("self_citation", 0) > 20:
        review["red_flags"].append("Heavy Self-Citation index. This can be flagged as 'Citation Gaming' by some reviewers.")
        
    if integrity_breakdown.get("outdated_datasets", 0) > 0:
        review["red_flags"].append("Usage of outdated/superseded benchmarks detected. Reviewers may question the relevance of performance gains on modern data.")

    return review
