import requests
import os

url = "http://localhost:8000/analyze"
pdf_path = [f for f in os.listdir("uploads") if f.endswith(".pdf")  and not f.startswith("highlight")][0]
pdf_path = os.path.join("uploads", pdf_path)

with open(pdf_path, 'rb') as f:
    files = {'file': (pdf_path, f, 'application/pdf')}
    data = {'doi': '10.1007/s10462-024-10810-6'}
    response = requests.post(url, files=files, data=data)
    
print(f"Status Code: {response.status_code}")
try:
    print(f"Response Analysis Mode: {response.json().get('analysis_mode')}")
    print(f"Cited by Count: {response.json().get('cited_by_count')}")
except:
    pass
