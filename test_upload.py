import requests

url = "http://localhost:8000/analyze"
with open('uploads/test.pdf', 'wb') as f:
    f.write(b"dummy pdf content")

with open('uploads/test.pdf', 'rb') as f:
    files = {'file': ('test.pdf', f, 'application/pdf')}
    data = {'doi': '10.1007/s10462-024-10810-6'}
    response = requests.post(url, files=files, data=data)
    
print(f"Status Code: {response.status_code}")
print(f"Raw Response: {response.text}")
