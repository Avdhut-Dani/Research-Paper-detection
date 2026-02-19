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
            "background information"
        ]

    def _map_label(self, top_label):
        mapping = {
            "solid research finding": "solid_claim",
            "vague or unconfident claim": "vague_claim",
            "research question or hypothesis": "question",
            "citation or reference": "citation",
            "background information": "background"
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

def is_actual_claim(sentence: str) -> bool:
    """
    Returns True if the sentence is either a solid or a vague claim.
    """
    res = get_detailed_classification(sentence)
    return res['label'] in ["solid_claim", "vague_claim"]
