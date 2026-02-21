from researcher_system.models.embedding_engine import embed
from sentence_transformers import util

def detect_false_citations(citation_contexts, cited_abstracts_map, similarity_threshold=0.3):
    """
    Detects potentially false citations by comparing the context sentence
    where the citation was made against the abstract of the cited paper.
    
    Args:
        citation_contexts (dict): { "citation_marker": ["context_sentence"...] }
        cited_abstracts_map (dict): { "citation_marker": "Abstract text from OpenAlex..." }
        similarity_threshold (float): Threshold below which a citation is flagged as suspicious.
        
    Returns:
        list of dict: Information on flagged false citations.
    """
    flagged_citations = []
    
    for citation, contexts in citation_contexts.items():
        abstract = cited_abstracts_map.get(citation)
        
        if not abstract:
            continue
            
        abstract_emb = embed([abstract])[0]
        
        for ctx in contexts:
            ctx_emb = embed([ctx])[0]
            sim_score = float(util.cos_sim(ctx_emb, abstract_emb))
            
            if sim_score < similarity_threshold:
                flagged_citations.append({
                    "citation": citation,
                    "context": ctx,
                    "abstract_snippet": abstract[:200] + "..." if len(abstract) > 200 else abstract,
                    "similarity_score": sim_score,
                    "reasoning": "Citation context sentence has very low semantic overlap with the cited paper's abstract."
                })
                
    return flagged_citations
