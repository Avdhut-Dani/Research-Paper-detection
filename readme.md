# Research Integrity & Misinformation Detection System

An advanced AI-powered ecosystem designed for institutional-level verification of research papers. This system automates the detection of academic misinformation, ranging from false citations and self-citation bias to unverified claims and outdated technical content.

---

## 🛑 The Problem: Misinformation in the "Publish or Perish" Era

In the modern academic landscape, the pressure to publish frequently leads to several critical issues:
*   **The "Publish or Perish" Culture**: The relentless drive for high publication counts often prioritizes quantity over quality, creating a breeding ground for intellectual shortcuts.
*   **The "PhD Pressure"**: Early-career researchers often face immense pressure to produce positive results, sometimes leading to "p-hacking" or the inclusion of unverified, vague claims to meet graduation requirements.
*   **Mentor-Mentee Frauds**: In some institutional settings, mentor-mentee relationships can become transactional, where unethical "citation cartels" are formed—researchers citing their mentors excessively (Self-Citation Bias) to artificially inflate H-index and institutional rankings.
*   **Information Decay**: Technical research moves at a lightning pace. Claims made in 2021 about "state-of-the-art AI" may be dangerous or misleading in 2026, yet they remain cited as current truth.
*   **False/Erroneous Citations**: Manual peer review often fails to verify if a cited paper *actually* supports the claim it’s attached to, allowing erroneous information to proliferate through the academic record.

---

## 🏛️ Our Solution: Institutional-Level Automated Verification

This project provides a robust, GPU-accelerated pipeline that "Stress Tests" a Research Paper before it reaches the final publication or submission stage. It acts as an automated "AI Peer Reviewer."

### Key Features & Current Progress
1.  **Semantic Claim Verification (RAG-Lite)**:
    Uses a Retrieval-Augmented Generation approach to compare extracted claims against the provided bibliography. It calculates **Semantic Relevance (0.0 - 1.0)** to identify if a citation is relevant or just a "placeholder."
2.  **Advanced Outdated Claim Architecture (Decay Model)**:
    Implements a sophisticated **10-step decay model**. Every claim is categorized (`FAST`, `MEDIUM`, `SLOW`, `TIMELESS`) to apply different **Half-Lives**. The system identifies "Moving Variables" (e.g., tech versions, market data) that accelerate aging.
3.  **Vague Claim Detection**:
    Identifies "Hedging" language (e.g., *"It might be possible..."*, *"We believe..."*) that often hides unverified or weak research findings.
4.  **Self-Citation Analysis**:
    Detects individual and institutional bias by calculating the ratio of self-references within the bibliography.
5.  **Interactive PDF Highlighting**:
    Automatically generates an annotated version of the research paper. 
    - 🟡 **Golden Yellow**: For solid, verified research findings.
    - 🔴 **OrangeRed**: For outdated claims that no longer hold true in the current year.
    - 🍑 **Light Peach**: For vague or unverified statements.

---

## 💻 Tech Stack & Component Deep-Dive

### **The Backend (Logic & AI)**
*   **FastAPI & Uvicorn**: A modern, high-performance web framework for Python. It handles the asynchronous intake of PDFs and manages the lifecycle of the analysis.
*   **Pathway**: A reactive data processing engine. It is used as a high-speed "Computational Table" to manage the relationship between thousands of words and their metadata.
*   **Hugging Face Transformers (`BART-Large-MNLI`)**: Our primary AI engine for **Zero-Shot Classification**. It categorizes claims into types (Solid, Vague, Outdated) without needing a pre-trained domain-specific database.
*   **PyTorch & CUDA**: The underlying deep learning backend. By using **CUDA Batching**, we parallelize claim analysis on the GPU, allowing the system to analyze 100+ claims in seconds.
*   **PyMuPDF (fitz)**: A high-performance PDF manipulation library used to read text coordinates and draw pixel-perfect highlight annotations.

### **The Frontend (UI/UX)**
*   **Vanilla HTML5/CSS3/JS**: Optimized for institutional deployment with **Dark Mode** support and reactive "Metric Cards" to display the **Integrity Score** and **Freshness Metrics**.
*   **Dynamic Badging System**: Each claim card in the UI provides deep metadata, including its **Stress Test status**, **Institutional Consensus**, and **Moving Variables**.

---

## 🧬 How it Works: The Mathematical Decay Model

We don't just check for "Old Papers." We detect **"Expired Knowledge."**
The system uses an adaptive freshness formula:
$$Freshness = \max(0, 100 \times (1 - \frac{Age}{HalfLife \times 2.5}))$$

Where:
- **Age** = Current Year - Support Citation Year.
- **Half-Life** = Determined by the category (e.g., AI/Tech: 1.5 years, Physics: 15 years).
- **Accelerator** = Increases based on the number of "Moving Variables" (like tech versions) found in the text.

---

## 🚀 Future Roadmap: Integrating the Next-Gen Stack

We aim to expand this into a global research integrity standard:
1.  **Global Cross-Reference (Step 11)**: Integration with the **Semantic Scholar API** and **CrossRef** to verify claims against the entire world's academic database, not just the uploaded paper's bibliography.
2.  **Institutional Graph Analysis**: Using **NetworkX** to map citation overlaps between different professors and PhD students to flag "Citation Cartels."
3.  **Hugging Face TGI (Text Generation Inference)**: Deploying the LLM via dedicated inference endpoints for faster, scalable institutional access.
4.  **Multi-Modal Analysis**: Extending support to analyze **Tables and Graphs** for statistical inconsistency (e.g., detecting if a graph doesn't match the textual claim).
5.  **Blockchain Integrity Log**: Recording the "Integrity Hash" of a paper on a private blockchain to prevent retrospective data tampering.

---
**Institutional Deployment Ready | Open Science Driven | AI-First Peer Review**