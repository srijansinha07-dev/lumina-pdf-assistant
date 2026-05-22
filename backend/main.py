"""
main.py — FastAPI application entry point.

Run with:
  python main.py
  OR
  uvicorn main:app --reload --port 8000
"""

print("MAIN.PY STARTED")

import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS

print("IMPORTING ROUTERS...")
from routers import chat, documents

print("IMPORTING DOCSTORE...")
from services import docstore

print("IMPORTS DONE")

app = FastAPI(
    title="PDF Assistant API",
    description="Local AI PDF assistant — OCR-aware RAG with hybrid retrieval.",
    version="1.0.0",
)

print("FASTAPI CREATED")

# ── CORS ───────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────
app.include_router(documents.router)
app.include_router(chat.router)


# ── Startup ────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    print("STARTUP HIT")
    print("SKIPPING DOCSTORE LOAD")
    print("✅ PDF Assistant API ready")


@app.get("/api/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
    )