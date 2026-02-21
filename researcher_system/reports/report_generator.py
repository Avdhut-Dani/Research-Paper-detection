def generate(res):
    print("\n=== UPGRADED ANALYSIS REPORT ===")
    print(f"Total Claims Found: {res.get('claims', 0)}")
    print(f"  - Solid Research Findings: {len(res.get('solid_claims', []))}")
    print(f"  - Vague or Unconfident Claims: {res.get('vague_claims', 0)}")
    print(f"Total Citations Extracted: {res.get('citations', 0)}")
    print(f"Average Citation Relevance: {res.get('avg_relevance', 0):.4f}")
    
    sc_ratio = res.get('self_citation_ratio', 0)
    sc_count = res.get('self_citation_count', 0)
    print(f"Self-Citation Ratio: {sc_ratio:.4f} ({sc_count} papers)")
    print(f"Integrity Score: {res.get('integrity_score', 0):.2f}")
    
    # False Citations
    fc = res.get('false_citations', [])
    if fc:
        print(f"\n--- ⚠️ False/Suspicious Citations ({len(fc)}) ---")
        for i, c in enumerate(fc[:3]):
            print(f"{i+1}. {c['citation']} (Sim: {c.get('similarity_score', 0):.2f}): {c.get('reasoning', '')}")
            
    # Datasets
    ds = res.get('datasets_found', [])
    if ds:
        print(f"\n--- 📊 Datasets Used ({len(ds)}) ---")
        print(", ".join(ds))
        out_ds = res.get('outdated_datasets', [])
        if out_ds:
            print("\n  ⚠️ Outdated Dataset Warnings:")
            for w in out_ds:
                print(f"  - {w['dataset']}: {w['reason']}")
    
    print("\n--- Top Solid Claims (with RAG and Freshness) ---")
    for i, sc in enumerate(res.get('solid_claims', [])[:5]):
        status = "✅" if sc.get('verified') else "❌"
        fresh = "⚠️ OUTDATED" if sc.get('is_outdated') else "🍃 FRESH"
        print(f"{i+1}. {status} {fresh} [{sc.get('decay_type','???')}] {sc['text']}")
        print(f"   Note: {sc.get('verification_note', '')}")

    print("\n--- Detailed Citations (Bibliography) ---")
    det_cit = res.get('detailed_citations', [])
    if det_cit:
        for i, cit in enumerate(det_cit[:3]):
            print(f"{i+1}. {cit['id']}")
            print(f"   Full Text: {cit['full_text'][:150]}...")
    else:
        print("No detailed citation list available.")
