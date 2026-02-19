def self_citation_ratio(citations,authors=["author"]):
    count=0
    for c in citations:
        if any(a.lower() in c.lower() for a in authors):
            count+=1
    return count/len(citations) if citations else 0
