from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid
from typing import Optional
from researcher_system.core.pipeline import run_pipeline

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from researcher_system.utils.pdf_highlighter import highlight_text_in_pdf

# ... (existing imports)

# Ensure uploads directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads") # Verify this is safe/needed or just return file response

@app.get("/")
def read_root():
    return JSONResponse(content={"message": "Welcome to Researcher System API. Go to /static/index.html for UI."})

@app.post("/analyze")
async def analyze_pdf(file: UploadFile = File(...), doi: Optional[str] = Form(None)):
    ext = file.filename.lower()
    if not (ext.endswith(".pdf") or ext.endswith(".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed.")

    file_id = str(uuid.uuid4())
    original_filename = file.filename
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{original_filename}")
    
    # Path for the highlighted PDF (if applicable)
    highlighted_filename = f"highlighted_{file_id}_{original_filename}" if ext.endswith(".pdf") else None
    highlighted_path = os.path.join(UPLOAD_DIR, highlighted_filename) if highlighted_filename else None

    try:
        # Rewind the file cursor. When FastAPI parses Form data alongside 
        # a File stream, the cursor may be advanced to the end.
        file.file.seek(0)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Run pipeline - pass doi if provided, and the original filename for title matching
        result = run_pipeline(file_path, doi=doi, filename=original_filename)
        
        # Prepare Highlighting Data
        # Solid Claims: Golden Yellow (1.0, 0.8, 0.0)
        # Outdated Claims: OrangeRed (1.0, 0.27, 0.0)
        highlights = []
        
        for sc in result.get('solid_claims', []):
            text = sc['text']
            color = (1.0, 0.27, 0.0) if sc.get('is_outdated') else (1.0, 0.8, 0.0)
            highlights.append((text[:150] if len(text) > 150 else text, color))
            
        for vc in result.get('vague_claims_list', []):
            text = vc['text']
            color = (1.0, 0.27, 0.0) if vc.get('is_outdated') else (1.0, 0.9, 0.7) # Light Peach for vague
            highlights.append((text[:150] if len(text) > 150 else text, color))
            
        # References are NOT highlighted now per user request

        # Highlight in PDF (Only for .pdf files)
        if highlights and ext.endswith(".pdf"):
             highlight_text_in_pdf(file_path, highlights, highlighted_path)
             result["highlighted_pdf_url"] = f"/uploads/{highlighted_filename}"
        
        # Cleanup original file
        if os.path.exists(file_path):
            os.remove(file_path)

        # Return the full result which now contains all frontend expected keys
        return JSONResponse(content=result)

    except Exception as e:
        # Cleanup on error
        if os.path.exists(file_path):
            os.remove(file_path)
        if highlighted_path and os.path.exists(highlighted_path):
             os.remove(highlighted_path)
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
