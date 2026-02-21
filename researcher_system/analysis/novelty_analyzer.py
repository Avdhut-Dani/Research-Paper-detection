import re

def analyze_novelty(text):
    """
    Analyzes the novelty claims of the paper.
    Detects: Contribution statements and specific novelty keywords.
    """
    results = {
        "contributions": [],
        "has_contribution_statement": False,
        "novelty_keywords": [],
        "has_scientific_gap": False,
        "gap_mentions": [],
        "is_novelty_specific": False
    }
    
    # 1. Detect Contribution Statements
    # Usually found near "Our contributions", "Specifically, we", "In this work, we propose"
    contribution_patterns = [
        r"(?i)our contributions (include|are|summarized as)?",
        r"(?i)the novelty of (our|this) (paper|work|method)",
        r"(?i)specifically, we",
        r"(?i)to the best of our knowledge, (this is )?the first",
        r"(?i)we provide (the )?first"
    ]
    
    # Let's extract sentences following these patterns
    sentences = re.split(r'(?<=[.!?])\s+', text)
    for i, sentence in enumerate(sentences):
        for pattern in contribution_patterns:
            if re.search(pattern, sentence):
                results["has_contribution_statement"] = True
                # Capture the sentence and maybe the next one if it exists
                context = sentence.strip()
                if i + 1 < len(sentences):
                    context += " " + sentences[i+1].strip()
                if context not in results["contributions"]:
                    results["contributions"].append(context)
                    
    # 2. Novelty Keywords
    novelty_words = [
        r"(?i)novel(ty)?",
        r"(?i)state-of-the-art",
        r"(?i)sota",
        r"(?i)outperform",
        r"(?i)superior",
        r"(?i)groundbreaking",
        r"(?i)pioneering"
    ]
    # 3. Detect Scientific Gap / Problem Motivation
    gap_patterns = [
        r"(?i)however, existing (methods|works|approaches) (fail to|lack|suffer from)",
        r"(?i)a major limitation (of|is)",
        r"(?i)this gap (remains|is)",
        r"(?i)unsolved problem",
        r"(?i)it is (not yet|unclear|difficult to)",
        r"(?i)to address these (limitations|issues|challenges)"
    ]
    results["has_scientific_gap"] = False
    results["gap_mentions"] = []
    for pattern in gap_patterns:
        matches = re.findall(pattern, text)
        if matches:
            results["has_scientific_gap"] = True
            results["gap_mentions"].extend(list(set(matches)))
            
    # 4. BERT-based Semantic Novelty Check
    results["is_novelty_specific"] = False
    if results["contributions"]:
        try:
            from sentence_transformers import SentenceTransformer, util
            model = SentenceTransformer('all-MiniLM-L6-v2') # lightweight but effective
            
            # Combine contributions
            contribution_text = " ".join(results["contributions"])
            
            # Extract a generic intro block (first 1000 chars excluding contributions)
            intro_block = text[:2000].replace(contribution_text, "")
            
            # Embed
            emb1 = model.encode(contribution_text, convert_to_tensor=True)
            emb2 = model.encode(intro_block, convert_to_tensor=True)
            
            # Check similarity. 
            # If the contribution is TOO similar (e.g. >0.8) to generic intro text, 
            # it might just be repeating the problem statement without proposing a specific solution.
            cos_sim = util.pytorch_cos_sim(emb1, emb2).item()
            
            # Specificity also requires some technical keyword presence
            feature_words = ["algorithm", "framework", "architecture", "benchmark", "dataset", "proof", "optimization", "model"]
            has_specifics = any(word in contribution_text.lower() for word in feature_words)
            
            # Novelty is specific if it differs from intro AND has technical keywords
            if cos_sim < 0.85 and has_specifics:
                results["is_novelty_specific"] = True
        except Exception as e:
            # Fallback for environment issues: use basic heuristics
            contribution_text = " ".join(results["contributions"])
            feature_words = ["algorithm", "framework", "architecture", "benchmark", "dataset", "proof", "optimization"]
            has_specifics = any(word in contribution_text.lower() for word in feature_words)
            results["is_novelty_specific"] = has_specifics and len(contribution_text.split()) > 20

    return results
