"""
routers/chat.py
───────────────
/api/chat — answer questions about a document.
Returns structured JSON with answer + sources.
"""
from __future__ import annotations

import re

from fastapi import APIRouter, HTTPException

from models import (
    ChatRequest, ChatResponse, ConfidenceLevel,
    IndexStatus, QueryType, Source,
)
from services import docstore
from services import llm as llm_svc
from services import retriever as ret_svc

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest):
    # ── Validate document ─────────────────────────────────────────────────
    info = docstore.get_info(req.doc_id)
    if not info:
        raise HTTPException(404, "Document not found.")
    if info.status != IndexStatus.READY:
        raise HTTPException(400, f"Document is not ready (status: {info.status}).")

    chunks = docstore.get_chunks(req.doc_id)
    pages  = docstore.get_pages(req.doc_id)

    # ── Retrieve ──────────────────────────────────────────────────────────
    result = ret_svc.retrieve(
        doc_id=req.doc_id,
        query=req.query,
        chunks=chunks,
        pages=pages,
    )

    # ── No results ────────────────────────────────────────────────────────
    if not result.chunks:
        fallback = _not_found_message(result.query_type, result.target_page)
        return ChatResponse(
            answer=fallback,
            query_type=result.query_type,
            sources=[],
        )

    # ── Build context for LLM ─────────────────────────────────────────────
    context_parts = []
    for i, c in enumerate(result.chunks):
        tag = "FORMULA" if c.has_formula else ("OCR" if c.ocr_sourced else "TEXT")
        context_parts.append(
            f"[Chunk {i+1} | Page {c.page} | {tag}]\n{c.text}"
        )
    context = "\n\n".join(context_parts)

    # ── Call LLM ──────────────────────────────────────────────────────────
    ocr_used = any(c.ocr_sourced for c in result.chunks)
    answer   = llm_svc.answer(
        query=req.query,
        context=context,
        qtype=result.query_type,
        page_num=result.target_page,
        ocr_used=ocr_used,
    )

    # ── Build sources ─────────────────────────────────────────────────────
    sources = []
    for c in result.chunks:
        sources.append(Source(
            doc_id=req.doc_id,
            doc_name=info.name,
            page=c.page,
            text=c.text[:400] + ("…" if len(c.text) > 400 else ""),
            ocr_sourced=c.ocr_sourced,
            confidence=_confidence(c.score, c.ocr_sourced),
        ))

    return ChatResponse(
        answer=answer,
        query_type=result.query_type,
        sources=sources,
    )


# ── Helpers ────────────────────────────────────────────────────────────────

def _not_found_message(qtype: QueryType, page: int | None) -> str:
    if qtype == QueryType.PAGE:
        return f"PAGE NOT FOUND:\n--------------\nPage {page} does not exist in the document."
    if qtype == QueryType.FORMULA:
        return "NOT FOUND:\n----------\nThe document does not explicitly contain this formula."
    return "The document does not explicitly contain this information."


def _confidence(score: float, ocr_sourced: bool) -> ConfidenceLevel:
    base = score
    if ocr_sourced:
        base -= 0.1   # slight penalty for OCR uncertainty
    if base >= 0.6:
        return ConfidenceLevel.HIGH
    if base >= 0.3:
        return ConfidenceLevel.MEDIUM
    return ConfidenceLevel.LOW
