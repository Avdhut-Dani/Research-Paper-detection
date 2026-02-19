def score(avg_rel,self_ratio,vague_count):
    return 100-(self_ratio*20+vague_count*2+(1-avg_rel)*30)
