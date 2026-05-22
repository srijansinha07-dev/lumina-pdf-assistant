# Lumina — Local AI PDF Assistant

Premium-looking, fully local AI PDF assistant with OCR-aware hybrid retrieval and strict anti-hallucination.

Built for academic/statistics PDFs containing formulas, equations, and LaTeX-rendered content.

---

## Features

- **Drag & drop PDF upload** with real-time indexing status
- **Hybrid retrieval**: semantic (ChromaDB) + keyword (BM25) + cross-encoder reranking
- **Smart OCR fallback**: automatically detects formula-only pages and OCRs them
- **Query classification**: PAGE / FORMULA / CONCEPT / EXACT routing
- **Anti-hallucination**: strict prompts that refuse to invent formulas
- **Page preview**: click "View source page" to see the rendered PDF page
- **Source citations**: every answer shows page, confidence, and supporting text
- **Dark premium UI**: Notion × Perplexity aesthetic

---

## Requirements

### System

- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.com) installed and running
- Tesseract OCR

### Install Tesseract

```bash
# Ubuntu / Debian
sudo apt install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download installer from https://github.com/UB-Mannheim/tesseract/wiki
```

### Pull Ollama models

```bash
ollama pull mistral
ollama pull nomic-embed-text
```

---

## Setup & Run

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Backend starts at **http://localhost:8000**

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend starts at **http://localhost:5173**

Open http://localhost:5173 in your browser.

---

## Project Structure

```
pdf-assistant/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # All configuration constants
│   ├── models.py                # Pydantic schemas + dataclasses
│   ├── requirements.txt
│   ├── routers/
│   │   ├── documents.py         # Upload, list, delete, page preview
│   │   └── chat.py              # Chat endpoint
│   └── services/
│       ├── extractor.py         # PyMuPDF + Tesseract OCR extraction
│       ├── chunker.py           # Formula-preserving paragraph chunker
│       ├── vectorstore.py       # ChromaDB + nomic-embed-text
│       ├── retriever.py         # Hybrid retrieval + query classification
│       ├── llm.py               # Ollama/Mistral prompt templates
│       └── docstore.py          # In-memory doc registry with JSON persistence
│
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── index.css
        ├── lib/
        │   ├── api.ts           # Typed axios API client
        │   └── utils.ts         # Helper functions
        ├── store/
        │   └── AppStore.tsx     # Global state (useReducer + Context)
        └── components/
            ├── layout/
            │   └── Sidebar.tsx  # Document list + upload zone
            ├── chat/
            │   ├── ChatPanel.tsx
            │   ├── ChatMessage.tsx
            │   ├── ChatInput.tsx
            │   └── SourceCard.tsx
            └── pdf/
                └── PagePreview.tsx
```

---

## Architecture

### Extraction Pipeline

```
PDF
 └─ PyMuPDF text extraction
      ├─ sufficient text? → use as-is
      └─ too few chars? → rasterise page → Tesseract OCR → merge
```

OCR threshold is 120 meaningful characters (configurable in `config.py`).
Only formula/image-heavy slides trigger OCR — normal text pages are never re-OCR'd.

### Retrieval Pipeline

```
Query
 └─ Classify: PAGE / FORMULA / CONCEPT / EXACT
      ├─ PAGE    → direct page lookup, skip embeddings
      ├─ FORMULA → semantic (formula chunks) + semantic (all) + BM25
      │             + formula/OCR score boosts + rerank
      └─ CONCEPT / EXACT → semantic + light BM25 + rerank
```

### Anti-Hallucination

- `temperature=0` on all LLM calls
- System prompt with 8 absolute rules
- Per query-type prompt templates with explicit NOT FOUND fallback format
- LLM is shown only retrieved context, never given prior chat history to fill gaps from

---

## Configuration (`backend/config.py`)

| Variable        | Default                              | Description                          |
|----------------|--------------------------------------|--------------------------------------|
| `OCR_THRESHOLD` | 120                                 | Chars below which OCR is triggered   |
| `OCR_DPI`       | 220                                 | Rasterisation DPI for OCR            |
| `TOP_K_SEMANTIC`| 10                                  | Semantic search candidates           |
| `TOP_K_BM25`    | 10                                  | BM25 keyword candidates              |
| `TOP_K_FINAL`   | 5                                   | Chunks sent to LLM after reranking   |
| `LLM_MODEL`     | `mistral`                           | Ollama model name                    |
| `EMBED_MODEL`   | `nomic-embed-text`                  | Ollama embedding model               |
| `RERANKER_MODEL`| `cross-encoder/ms-marco-MiniLM-L-6-v2` | Local cross-encoder reranker      |

---

## Troubleshooting

**"Ollama error" on startup**
→ Make sure Ollama is running: `ollama serve`
→ Pull models: `ollama pull mistral && ollama pull nomic-embed-text`

**Tesseract not found**
→ Install system package (see Requirements above)
→ OCR will be disabled but the app still works for text-extractable PDFs

**Reranker slow on first run**
→ The cross-encoder model (~22MB) downloads once from HuggingFace on first use.
→ No GPU needed — runs fine on CPU.

**Formula not found even after OCR**
→ Some formulas are too complex for Tesseract (e.g. multi-line integrals).
→ Increase `OCR_DPI` in config.py to 280 for better accuracy.
→ You can also click "View source page" to see the rendered page and read formulas visually.

**Re-index a document after config changes**
→ Delete the document in the UI (trash icon), then re-upload it.
→ Or manually delete `backend/chroma_db/` and `backend/uploads/documents.json`.
