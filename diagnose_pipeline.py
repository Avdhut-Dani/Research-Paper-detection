from researcher_system.nlp.pdf_parser import extract_text
from researcher_system.core.pipeline import run_pipeline
from researcher_system.core.config import PAPER_PATH
import json

def diagnose():
    print(f"Diagnosing PDF: {PAPER_PATH}")
    
    # Check text extraction
    parsed = extract_text(PAPER_PATH)
    print("\n--- EXTRACTION STATS ---")
    print(f"Body length: {len(parsed['body'])}")
    print(f"References length: {len(parsed['references'])}")
    
    if len(parsed['body']) < 100:
        print("WARNING: Body text is suspiciously short!")
    if len(parsed['references']) == 0:
        print("WARNING: No references section found!")

    # Check full pipeline
    print("\n--- PIPELINE OUTPUT ---")
    result = run_pipeline(PAPER_PATH)
    
    # We remove large redundant data for clean print
    clean_res = {k: v for k, v in result.items() if k not in ['bibliography', 'solid_claims', 'vague_claims', 'detailed_citations']}
    print(json.dumps(clean_res, indent=2))
    
    print("\n--- SAMPLE CLAIMS ---")
    print(f"Solid Claims Count: {len(result['solid_claims'])}")
    for sc in result['solid_claims'][:2]:
        print(f" - {sc['text'][:100]}...")

    print(f"\nVague Claims Count: {len(result['vague_claims'])}")
    for vc in result['vague_claims'][:2]:
        print(f" - {vc['text'][:100]}...")

if __name__ == "__main__":
    diagnose()
