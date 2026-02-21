import re
import logging

# Global model cache to prevent reloading on every request
_MODEL_CACHE = {}

def get_bert_model():
    if 'model' not in _MODEL_CACHE:
        try:
            from sentence_transformers import SentenceTransformer
            _MODEL_CACHE['model'] = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            logging.error(f"Failed to load SentenceTransformer: {e}")
            _MODEL_CACHE['model'] = None
    return _MODEL_CACHE['model']

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
    contribution_patterns = [
        r"(?i)our contributions (include|are|summarized as)?",
        r"(?i)the novelty of (our|this) (paper|work|method)",
        r"(?i)specifically, we",
        r"(?i)to the best of our knowledge, (this is )?the first",
        r"(?i)we provide (the )?first",
        r"(?i)we propose",
        r"(?i)we introduce",
        r"(?i)in this paper, we",
        r"(?i)main contribution(s)?",
        r"(?i)fundamental shift",
        r"(?i)novel method",
    ]
    
    sentences = re.split(r'(?<=[.!?])\s+', text)
    for i, sentence in enumerate(sentences):
        for pattern in contribution_patterns:
            if re.search(pattern, sentence):
                results["has_contribution_statement"] = True
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
        r"(?i)to address these (limitations|issues|challenges)",
        r"(?i)despite (its|their) success",
        r"(?i)hard to scale",
        r"(?i)inefficient"
    ]
    for pattern in gap_patterns:
        matches = re.findall(pattern, text)
        if matches:
            results["has_scientific_gap"] = True
            if isinstance(results["gap_mentions"], list):
                results["gap_mentions"].extend(list(set(matches)))
            
    # 4. BERT-based Semantic Novelty Check
    model = get_bert_model()
    if results["contributions"] and model:
        try:
            from sentence_transformers import util
            
            contribution_text = " ".join(results["contributions"])
            intro_block = text[:2000].replace(contribution_text, "")
            
            emb1 = model.encode(contribution_text, convert_to_tensor=True)
            emb2 = model.encode(intro_block, convert_to_tensor=True)
            
            cos_sim = util.pytorch_cos_sim(emb1, emb2).item()
            
            feature_words = ["algorithm", "framework", "architecture", "benchmark", "dataset", "proof", "optimization", "model"]
            has_specifics = any(word in contribution_text.lower() for word in feature_words)
            
            if cos_sim < 0.85 and has_specifics:
                results["is_novelty_specific"] = True
        except Exception as e:
            logging.warning(f"Feature specific check failed: {e}")

    # Final fallback if BERT failed or was N/A
    if not results["is_novelty_specific"] and results["contributions"]:
        contribution_text = " ".join(results["contributions"])
        feature_words = ["algorithm", "framework", "architecture", "benchmark", "dataset", "proof", "optimization"]
        has_specifics = any(word in contribution_text.lower() for word in feature_words)
        results["is_novelty_specific"] = has_specifics and len(contribution_text.split()) > 20

    return results
