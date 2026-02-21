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

from researcher_system.utils.pdf_highlighter import highlight_text_in_pdf, merge_pdfs
from researcher_system.utils.pdf_report_generator import generate_summary_page
from researcher_system.utils.converter_utils import convert_docx_to_pdf

# Ensure uploads directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
def read_root():
    return JSONResponse(content={"message": "Welcome to Researcher System API."})

@app.post("/analyze")
async def analyze_pdf(file: UploadFile = File(...), doi: Optional[str] = Form(None)):
    ext = file.filename.lower()
    if not (ext.endswith(".pdf") or ext.endswith(".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed.")

    file_id = str(uuid.uuid4())
    original_filename = file.filename
    temp_path = os.path.join(UPLOAD_DIR, f"temp_{file_id}_{original_filename}")
    
    try:
        file.file.seek(0)
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 1. Processing Pathway (Conversion if needed)
        analysis_path = temp_path
        working_pdf_path = temp_path if ext.endswith(".pdf") else None
        
        if ext.endswith(".docx"):
            working_pdf_path = convert_docx_to_pdf(temp_path, UPLOAD_DIR)
            if not working_pdf_path:
                raise Exception("Conversion to PDF failed.")
        
        # 2. Run Pipeline
        result = run_pipeline(temp_path, doi=doi, filename=original_filename)
        
        # 3. Comprehensive Highlighting Schema
        highlights = []
        
        # Red: False Citations and Vague Claims (Risks)
        accent_red = (0.93, 0.26, 0.26)
        for fc in result.get('false_citations', []):
            highlights.append((fc['context'], accent_red))
        for vc in result.get('vague_claims_list', []):
            highlights.append((vc['text'][:150], accent_red))
            
        # Green: Novelty & Contributions
        accent_green = (0.06, 0.72, 0.5)
        novelty = result.get('system_review', {}).get('novelty', {}) or {}
        contributions = result.get('novelty', {}).get('contributions', []) if isinstance(result.get('novelty'), dict) else []
        for c_text in contributions:
            highlights.append((c_text[:150], accent_green))
            
        # Blue: Rigor (Ablation, Baselines)
        accent_blue = (0.23, 0.51, 0.96)
        # Pull from rigor_analyzer findings if possible (we might need to store direct text matches in result)
        # For now, we'll highlight solid claims if they aren't processed as novelty
        for sc in result.get('solid_claims', []):
            highlights.append((sc['text'][:150], accent_blue))
            
        # Purple: Datasets
        accent_purple = (0.54, 0.36, 0.96)
        for ds in result.get('datasets_found', []):
            highlights.append((ds, accent_purple))

        # 4. Generate Highlighted Body
        highlighted_body_path = os.path.join(UPLOAD_DIR, f"hbody_{file_id}.pdf")
        if highlights and working_pdf_path:
            highlight_text_in_pdf(working_pdf_path, highlights, highlighted_body_path)
        else:
            highlighted_body_path = working_pdf_path if working_pdf_path else None

        # 5. Generate Summary Page
        summary_page_path = os.path.join(UPLOAD_DIR, f"summary_{file_id}.pdf")
        generate_summary_page(result, summary_page_path)

        # 6. Merge Summary + Body
        final_filename = f"report_{file_id}_{original_filename.rsplit('.', 1)[0]}.pdf"
        final_path = os.path.join(UPLOAD_DIR, final_filename)
        
        merge_pdfs([summary_page_path, highlighted_body_path], final_path)
        
        result["highlighted_pdf_url"] = f"/uploads/{final_filename}"
        
        # Cleanup temp files
        for p in [temp_path, working_pdf_path, highlighted_body_path, summary_page_path]:
            if p and os.path.exists(p) and p != final_path:
                try: os.remove(p)
                except: pass

        return JSONResponse(content=result)

    except Exception as e:
        if os.path.exists(temp_path): os.remove(temp_path)
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
