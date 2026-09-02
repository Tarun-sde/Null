from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse
from app.services.chat_assistant_service import process_chat_message
from app.core.config import settings

from fastapi.responses import StreamingResponse
from app.services.chat_assistant_service import process_chat_message, stream_chat_message

router = APIRouter(prefix="/chat", tags=["AI Assistant"])


@router.post("", response_model=ChatMessageResponse)
def send_chat_message(
    req: ChatMessageRequest,
    db: Session = Depends(get_db),
):
    """
    Query the grounded RentSense AI Operations Assistant (Synchronous).
    """
    history_payload = (
        [{"role": h.role, "content": h.content} for h in req.history]
        if req.history
        else []
    )
    result = process_chat_message(db=db, message=req.message, history=history_payload)
    return ChatMessageResponse(
        reply=result["reply"],
        is_configured=result.get("is_configured", True),
        grounded=result.get("grounded", True),
        model=result.get("model", settings.GEMINI_MODEL),
    )


@router.post("/stream")
def stream_chat(
    req: ChatMessageRequest,
    db: Session = Depends(get_db),
):
    """
    Stream grounded AI response chunks via Server-Sent Events (SSE).
    Dramatically improves perceived latency by delivering initial tokens in ~500ms.
    """
    history_payload = (
        [{"role": h.role, "content": h.content} for h in req.history]
        if req.history
        else []
    )
    return StreamingResponse(
        stream_chat_message(db=db, message=req.message, history=history_payload),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/status")
def get_assistant_status():
    """
    Check if the AI Assistant is configured with a Gemini API key.
    """
    is_conf = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip())
    return {
        "is_configured": is_conf,
        "model": settings.GEMINI_MODEL,
    }
