def generate(res):
    print("\n=== UPGRADED ANALYSIS REPORT ===")
    print(f"Total Claims Found: {res['claims_count']}")
    print(f"  - Solid Research Findings: {res['solid_claims_count']}")
    print(f"  - Vague or Unconfident Claims: {res['vague_claims_count']}")
    print(f"Total Citations Extracted: {res['citations_count']}")
    print(f"Average Citation Relevance: {res['avg_relevance']:.4f}")
    print(f"Self-Citation Ratio: {res['self_citation_ratio']:.4f}")
    print(f"Integrity Score: {res['integrity_score']:.2f}")
    
    print("\n--- Top Solid Claims (with RAG Verification) ---")
    for i, sc in enumerate(res['solid_claims'][:5]):
        status = "✅" if sc['verified'] else "❌"
        print(f"{i+1}. {status} {sc['text']}")
        print(f"   Note: {sc['verification_note']}")

    print("\n--- Vague Claims Detected ---")
    for i, vc in enumerate(res['vague_claims'][:5]):
        print(f"{i+1}. ⚠️ {vc['text']}")

    print("\n--- Detailed Citations (Bibliography) ---")
    if 'detailed_citations' in res:
        for i, cit in enumerate(res['detailed_citations'][:3]):
            print(f"{i+1}. {cit['id']}")
            print(f"   Full Text: {cit['full_text'][:150]}...")
    else:
        print("No detailed citation list available.")
