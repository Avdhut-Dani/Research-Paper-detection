import os
from researcher_system.api.openalex_client import fetch_paper_by_doi
from researcher_system.core.pipeline import fuzzy_match_titles

doi = "10.1007/s10462-024-10810-6"
filename = "Deepfake video detection challenges and opportunities.pdf"

print("1. Extracting metadata from OpenAlex")
temp_metadata = fetch_paper_by_doi(doi)

print("2. Matching filename to API Title")
pdf_title = os.path.splitext(filename)[0].replace("_", " ")
print(f"API Title: {temp_metadata.get('title')}")
print(f"Filename Title: {pdf_title}")

if fuzzy_match_titles(pdf_title, temp_metadata.get("title", "")):
    print("Mode: MATCHED_HYBRID")
else:
    print("Mode: MATCHED_HYBRID_WARN")
