# Project Report: Researcher System

## 1. Executive Summary
The **Researcher System** is an AI-powered pipeline designed to analyze academic papers (PDFs), extract key claims and citations, verify their integrity, and present the results through an interactive web interface. The system leverages state-of-the-art NLP models for semantic understanding and provides visual feedback by highlighting verified claims directly within the source document.

## 2. Technical Architecture & Tech Stack

### core Technology
- **Language**: Python 3.12+
- **Framework**: FastAPI (Backend API), HTML5/CSS3/JS (Frontend)

### Modules & Libraries

| component | Technology Used | Purpose |
| :--- | :--- | :--- |
| **PDF Parsing** | `PyPDF2` | Extracts raw text content from PDF documents for initial processing. |
| **Claim Segmentation** | `spaCy` (`en_core_web_sm`) | Segments continuous text into individual sentences and linguistic units to identify potential claims. |
| **Citation Extraction** | [re](cci:1://file:///home/avdhut-dani/Desktop/Programming/CUDA%20Pojects/test_model_paper_citation/app.py:32:0-34:114) (Regular Expressions) | Identifies citations using custom patterns (Bracket `[1]` & Author-Year [(Author, 2020)](cci:1://file:///home/avdhut-dani/Desktop/Programming/CUDA%20Pojects/test_model_paper_citation/researcher_system/reports/report_generator.py:0:0-14:81) styles). |
| **Semantic Analysis** | `SentenceTransformers` (`all-MiniLM-L6-v2`) | Converts claims and citations into dense vector embeddings to calculate semantic similarity. |
| **Vector Computation** | `PyTorch` / `CUDA` | Accelerates embedding generation and cosine similarity calculations on supported GPUs. |
| **Integrity Scoring** | Custom Algorithm | Calculates a composite score based on claim relevance, vagueness, and self-citation ratios. |
| **PDF Highlighting** | `PyMuPDF` (`fitz`) | Locates exact text coordinates in the PDF and applies yellow highlight annotations for visual verification. |
| **API Server** | `FastAPI` + `Uvicorn` | Provides high-performance, asynchronous endpoints for file uploads and analysis results. |

## 3. Methodology: How It Works

The system follows a linear pipeline architecture ([researcher_system/core/pipeline.py](cci:7://file:///home/avdhut-dani/Desktop/Programming/CUDA%20Pojects/test_model_paper_citation/researcher_system/core/pipeline.py:0:0-0:0)):

1. **Ingestion**: The user uploads a PDF via the Web UI.
2. **Text Extraction**: [pdf_parser.py](cci:7://file:///home/avdhut-dani/Desktop/Programming/CUDA%20Pojects/test_model_paper_citation/researcher_system/nlp/pdf_parser.py:0:0-0:0) reads the binary PDF stream and converts it to a string.
3. **NLP Segmentation**:
    - `claim_segmenter.py` uses spaCy to break text into sentences.
    - [citation_extractor.py](cci:7://file:///home/avdhut-dani/Desktop/Programming/CUDA%20Pojects/test_model_paper_citation/researcher_system/nlp/citation_extractor.py:0:0-0:0) scans for references using regex patterns (e.g., `[1]`, [(Smith et al., 2020)](cci:1://file:///home/avdhut-dani/Desktop/Programming/CUDA%20Pojects/test_model_paper_citation/researcher_system/reports/report_generator.py:0:0-14:81)).
4. **Analysis**:
    - **Relevance**: `semantic_relevance.py` encodes claims and citations into vectors and computes their cosine similarity to determine if claims are supported by citations.
    - **Vague Detection**: `vague_detector.py` checks for weak language (e.g., "suggests", "might") to flag unconfident claims.
    - **Self-Citation**: `self_citation_analysis.py` calculates the ratio of self-references to detect potential bias.
5. **Score Calculation**: `integrity_scoring.py` aggregates these metrics into a final "Integrity Score" (0-100).
6. **Highlighting**: [pdf_highlighter.py](cci:7://file:///home/avdhut-dani/Desktop/Programming/CUDA%20Pojects/test_model_paper_citation/researcher_system/utils/pdf_highlighter.py:0:0-0:0) searches the original PDF for the identified high-value claims and creates a new, annotated PDF.
7. **Presentation**: The Web UI displays metrics, lists claims/citations, and offers the highlighted PDF for download.

## 4. Design Justification

### Why Local Models?
- **Privacy**: No data leaves the server; ideal for confidential research.
- **Cost**: Zero inference cost compared to paid APIs like OpenAI or Anthropic.
- **Latency**: `all-MiniLM-L6-v2` is extremely fast and optimized for semantic similarity tasks, running in milliseconds on consumer hardware.

### Why FastAPI?
- **Async Efficiency**: Handles file uploads and concurrent processing requests better than synchronous frameworks like Flask.
- **Modern Standards**: Automatic OpenAPI documentation and type safety via Pydantic.

### Why Regex + Embeddings?
- **Hybrid Approach**: Regex provides high precision for structured data (citations), while embeddings provide high recall and understanding for unstructured text (claims), offering the best of both worlds.

## 5. Comparison with Existing Solutions

| Feature | **Researcher System** | **Keyword Search (Ctrl+F)** | **LLM-based (ChatGPT)** |
| :--- | :--- | :--- | :--- |
| **Context Awareness** | High (Semantic Vectors) | Low (Exact Match) | Very High |
| **Integrity Checks** | Yes (Scoring Logic) | No | Limited (Hallucinations) |
| **Visual Feedback** | **Yes (Highlighter)** | Yes (Browser Find) | No (Text Only) |
| **Cost** | Free (Local Compute) | Free | High (Token Costs) |
| **Privacy** | Local / Offline | Local | Cloud / Shared |

## 6. Future Upgrades & Roadmap

To further enhance the system, we propose the following upgrades:

1. **Cross-Ref Verification**: Integrating with external APIs (e.g., Semantic Scholar, CrossRef) to verify if citations actually support the claims (checking the ground truth).
2. **Graph Analysis**: Using `networkx` to visualize citation networks and identify "circular reporting" or citation cartels.
3. **Advanced Models**: Upgrading to larger embedding models (e.g., `all-mpnet-base-v2`) for better nuance detection, or fine-tuning a model on scientific literature.
4. **OCR Capability**: Integrating `Tesseract` or `PaddleOCR` to handle scanned PDFs that lack a text layer.
5. **Multi-Paper Analysis**: Allowing users to upload a batch of papers to find conflicting or supporting evidence across documents.

---
*Report Generated: 2026-02-13*