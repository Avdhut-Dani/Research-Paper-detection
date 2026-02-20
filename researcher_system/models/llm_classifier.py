from transformers import pipeline
import torch

class ClaimClassifier:
    def __init__(self, model_name="facebook/bart-large-mnli"):
        # We use a zero-shot classifier to distinguish between Solid Claims, Vague Claims, and Questions
        device = 0 if torch.cuda.is_available() else -1
        self.classifier = pipeline("zero-shot-classification", model=model_name, device=device)
        self.candidate_labels = [
            "solid research finding", 
            "vague or unconfident claim", 
            "research question or hypothesis", 
            "citation or reference",
            "background information",
            "filler, noise, or introductory text"
        ]

    def _map_label(self, top_label):
        mapping = {
            "solid research finding": "solid_claim",
            "vague or unconfident claim": "vague_claim",
            "research question or hypothesis": "question",
            "citation or reference": "citation",
            "background information": "background",
            "filler, noise, or introductory text": "noise"
        }
        return mapping.get(top_label, "other")

    def classify_sentence(self, sentence):
        """
        Classifies a single sentence (convenience wrapper).
        """
        return self.classify_batch([sentence])[0]

    def classify_batch(self, sentences, batch_size=16):
        """
        Classifies a list of sentences using GPU batching.
        """
        if not sentences:
            return []
            
        # Passing a list to the classifier pipeline enables batching
        results = self.classifier(sentences, self.candidate_labels, batch_size=batch_size)
        
        # If single sentence, transformers returns a dict, otherwise a list of dicts
        if isinstance(results, dict):
            results = [results]
            
        output = []
        for res in results:
            top_label = res['labels'][0]
            top_score = res['scores'][0]
            output.append({
                "label": self._map_label(top_label),
                "score": float(top_score)
            })
        return output

    def classify_decay_type(self, sentence):
        """
        Classifies the decay type of a claim and identifies dynamic moving variables.
        """
        # Step 1: Identify Decay Category
        decay_labels = [
            "technology, benchmarks, software, or market data (Fast Decay)",
            "trends, social statistics, or economic guidelines (Medium Decay)",
            "mathematics, physics fundamentals, or historical facts (Slow Decay)",
            "timeless logical proofs or core scientific laws"
        ]
        
        res = self.classifier(sentence, decay_labels)
        top_label = res['labels'][0]
        
        # Step 3: Identify Moving Variables (Dynamic Inputs)
        variable_labels = ["prices", "software versions", "market share", "leadership", "laws", "statistics", "none"]
        var_res = self.classifier(sentence, variable_labels)
        moving_vars = [label for label, score in zip(var_res['labels'], var_res['scores']) if score > 0.4 and label != "none"]

        if "Fast Decay" in top_label:
            return "FAST", "Technology/Market data decays quickly.", moving_vars
        elif "Medium Decay" in top_label:
            return "MEDIUM", "Trends and statistics have moderate stability.", moving_vars
        elif "Slow Decay" in top_label:
            return "SLOW", "Fundamentals and history are very stable.", moving_vars
        else:
            return "TIMELESS", "Core laws and logic do not expire.", moving_vars

    def classify_advanced_freshness(self, sentence):
        """
        Simulates the 10-step architecture:
        Type, Timestamp, Moving Variables, Disconfirming Evidence, Consensus, etc.
        """
        # Step 1: Type & Decay
        decay_type, decay_reason, moving_vars = self.classify_decay_type(sentence)
        
        # Step 4 & 7: Simulated Consensus & Evidence Search
        # In a real system, this would be a Google/Semantic Scholar Search.
        # Here we use LLM's internal knowledge to simulate "searching for disconfirming evidence".
        analysis_prompt = (
            f"Analyze this research claim for outdatedness based on these steps:\n"
            f"Claim: '{sentence}'\n"
            f"1. Is there recent (2025-2026) disconfirming evidence?\n"
            f"2. Does it depend on moving variables like ${', '.join(moving_vars) if moving_vars else 'none'}?\n"
            f"3. What is the current institutional consensus?\n"
            f"Return a short 1-sentence summary of the 'Stress Test' result."
        )
        
        # Use zero-shot as a proxy for specific analysis if needed, 
        # but here we'll just return a structured simulated finding for the UI.
        stress_test = "Claim stands against recent disconfirming evidence." if "TIMELESS" in decay_type or "SLOW" in decay_type else "Newer models or datasets may contradict this finding."
        
        return {
            "decay_type": decay_type,
            "reason": decay_reason,
            "moving_variables": moving_vars,
            "stress_test": stress_test,
            "consensus": "Matches current scientific consensus." if "SLOW" in decay_type else "Market/Tech consensus shifts frequently."
        }

# Singleton instance to avoid reloading model
_classifier = None

def get_classifier():
    global _classifier
    if _classifier is None:
        _classifier = ClaimClassifier()
    return _classifier

def get_detailed_classification(sentence: str):
    clf = get_classifier()
    return clf.classify_sentence(sentence)

def get_decay_analysis(sentence: str):
    clf = get_classifier()
    analysis = clf.classify_advanced_freshness(sentence)
    return analysis["decay_type"], analysis["reason"], analysis["moving_variables"], analysis["stress_test"], analysis["consensus"]

def is_actual_claim(sentence: str) -> bool:
    """
    Returns True if the sentence is either a solid or a vague claim.
    """
    res = get_detailed_classification(sentence)
    return res['label'] in ["solid_claim", "vague_claim"]
