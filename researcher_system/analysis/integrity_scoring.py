def score(avg_rel,self_ratio,vague_count):
    raw = 100-(self_ratio*25 + vague_count*1.5 + (1-avg_rel)*30)
    return max(0, min(100, raw))
