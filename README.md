# SmartNotice — Agentic Document Routing System for Colleges

An AI-powered pipeline that ingests unstructured documents (PDFs, 
scanned images, emails) and automatically extracts, classifies, 
and routes college notices to the right destinations — 
notice boards, SMS, WhatsApp, and college ERPs.

## What it does
- Reads any document type — PDF, image, email, text
- Classifies whether it is a valid college notice
- Extracts structured fields using Google Gemini AI
- Routes notices based on type, audience, and urgency
- Flags low-confidence documents for human review

## Tech Stack
- Python 3.10+
- Google Gemini 1.5 Flash (AI extraction)
- Instructor + Pydantic (structured output validation)
- pdfplumber (PDF parsing)
- Tesseract OCR (image/scan parsing)
- LangGraph (routing agent) — Stage 3
- Streamlit (admin dashboard) — Stage 5

## Project Structure
college_notice_system/
├── inputs/              # Drop documents here
├── outputs/             # Extracted JSON saved here
├── stage1_extractor.py  # Document ingestion and OCR
├── stage2_extractor.py  # AI field extraction
├── .env.example         # API key template
└── README.md

## Pipeline Stages
| Stage | Description | Status |
|-------|-------------|--------|
| Stage 1 | Document ingestion and text extraction |  Done |
| Stage 2 | AI-powered field extraction |  Done |
| Stage 3 | Agentic routing engine |  In progress |
| Stage 4 | Output delivery (SMS, WhatsApp, web) |  Upcoming |
| Stage 5 | Admin dashboard |  Upcoming |

## Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/smartnotice.git
cd smartnotice
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your API key
```bash
cp .env.example .env
# Open .env and add your Gemini API key
```

### 5. Install Tesseract OCR
Download from: https://github.com/UB-Mannheim/tesseract/wiki
Install to default path: `C:\Program Files\Tesseract-OCR\`

### 6. Run the pipeline
```bash
# Stage 1 — extract text from documents
python stage1_extractor.py

# Stage 2 — AI extraction
python stage2_extractor.py
```

## Environment Variables
GEMINI_API_KEY=your_key_here

## Author
Built as a GenAI capstone project — Unstructured Data Routing System
