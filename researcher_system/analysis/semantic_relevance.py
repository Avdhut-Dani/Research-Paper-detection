from researcher_system.models.embedding_engine import embed
from sentence_transformers import util

def relevance(c,e):
    e1=embed([c])
    e2=embed([e])
    return float(util.cos_sim(e1,e2))
