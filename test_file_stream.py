from fastapi import FastAPI, File, UploadFile, Form
from fastapi.testclient import TestClient
from typing import Optional
import os

app = FastAPI()

@app.post("/test")
async def test_upload(file: UploadFile = File(...), doi: Optional[str] = Form(None)):
    # Crucial fix: rewind the file pointer to the beginning before saving!
    file.file.seek(0)
    
    path = f"tmp_{file.filename}"
    with open(path, "wb") as buffer:
        import shutil
        shutil.copyfileobj(file.file, buffer)
        
    size = os.path.getsize(path)
    os.remove(path)
    return {"size": size, "doi": doi}

client = TestClient(app)

with open("uploads/test.pdf", "wb") as f:
    f.write(b"this is a dummy test file for size checking")

with open("uploads/test.pdf", "rb") as f:
    resp1 = client.post("/test", files={"file": ("test.pdf", f, "application/pdf")})
print("No DOI size:", resp1.json())

with open("uploads/test.pdf", "rb") as f:
    resp2 = client.post("/test", files={"file": ("test.pdf", f, "application/pdf")}, data={"doi": "123"})
print("With DOI size:", resp2.json())
