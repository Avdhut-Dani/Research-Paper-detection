# 🛠 Research PDF Analyzer: Technical Stack Deep-Dive

This document provides a exhaustive, component-level breakdown of every technology used in the project and its specific role in the Research Integrity & Misinformation Detection pipeline.

---

## 1. Core Execution Layer
### **Python 3.12+**
The entire system is built on Python, chosen for its vast ecosystem of AI, NLP, and scientific computing libraries. It serves as the "glue" that connects the web server to the deep learning models.

### **FastAPI & Uvicorn**
*   **Role**: Web Server & API Backbone.
*   **Function**: FastAPI manages the high-performance asynchronous endpoints (`/analyze`, `/uploads`). It allows for non-blocking file handling, meaning the server can process one PDF's text while another is still being uploaded. Uvicorn acts as the lightning-fast ASGI server implementation.

---

## 2. Artificial Intelligence & NLP Engine
### **Hugging Face Transformers (`facebook/bart-large-mnli`)**
*   **Role**: The "Analytical Brain."
*   **Function**: We use the **BART Large MNLI** model for **Zero-Shot Classification**. 
    *   **Why?**: Traditional classifiers need to be trained on thousands of examples. Zero-shot can classify a sentence as a "Solid Research Finding" or "Vague Claim" simply by understanding the *semantic concept* of those labels.
    *   **Logic**: It handles the "Misinformation Gatekeeping" by identifying filler text (noise), weak language (vague claims), and solid evidence.

### **Sentence-Transformers (`all-MiniLM-L6-v2`)**
*   **Role**: Semantic Similarity Engine.
*   **Function**: This model converts sentences into 384-dimensional dense vectors (embeddings).
    *   **Application**: We use it to compare a **Claim** in the text to its **Supporting Citation** in the bibliography. If the vector distance is large, the system flags the citation as potentially irrelevant or false support.

### **SpaCy (`en_core_web_sm`)**
*   **Role**: Linguistic Pre-processor.
*   **Function**: Splits raw PDF text into logical sentences. Unlike simple regex, SpaCy understands sentence boundaries (avoiding splits at "e.g." or "Fig. 1").

---

## 3. Data Processing & Computation
### **Pathway**
*   **Role**: Reactive Data Processing.
*   **Function**: Acts as a high-speed "Computational Table." It manages the extracted claims, citations, and metadata in a table structure that allows for fast filtering, joining, and batch processing of research data.

### **PyTorch & CUDA**
*   **Role**: Hardware Acceleration (GPU).
*   **Function**: Every AI model in this project is executed via PyTorch. We leverage **NVIDIA CUDA** to perform **GPU Batching**.
    *   **Performance**: Instead of analyzing sentences one by one on the CPU (taking minutes), we push them in batches of 16 to the GPU, reducing total analysis time to seconds.

---

## 4. PDF Manipulation & Visualization
### **PyMuPDF (`fitz`)**
*   **Role**: PDF Parser & Annotator.
*   **Function**: 
    1.  **Extraction**: Reads the binary content of the PDF and extracts plain text while maintaining coordinate data.
    2.  **Highlighting**: Once a claim is analyzed, `fitz` calculates the precise pixel coordinates on the page and draws **RGBA highlights** (e.g., OrangeRed for outdated content, Golden for solid findings).

---

## 5. Architectural Algorithms
### **10-Step Adaptive Decay Model**
*   **Logic**: A custom implementation that uses LLM classification to assign "Half-Lives" to claims.
*   **Parameters**: Fast/Medium/Slow decay types, Moving Variables (tech specs, versions), and Institutional Consensus checks.

### **Weighted Integrity Scoring**
*   **Logic**: A composite algorithm that combines:
    - **Self-Citation Ratio** (Bias check)
    - **Vagueness Density** (Certainty check)
    - **Freshness Score** (Temporal validity)
    - **Semantic Relevance** (Citation accuracy)

---

## 6. Frontend Stack
### **Vanilla HTML5, CSS3, ES6 JavaScript**
*   **Role**: Interactive Dashboard.
*   **Technologies**:
    - **CSS Variables**: Power the dynamic Dark/Light mode.
    - **Fetch API**: Handles the asynchronous communication with the FastAPI backend without page reloads.
    - **Dynamic DOM Injection**: Injects claim "cards" with badges for Decay Type, Stress Tests, and Consensus results.

---

## 7. Development & Deployment
### **Git/GitHub**
*   **Role**: Version Control.
*   **Function**: Manages the collaborative code state and tracks the evolution of the integrity detection heuristics.

---
**Institutional Grade | GPU Optimized | Powered by Open Science**
