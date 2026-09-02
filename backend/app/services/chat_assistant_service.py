"""
Optimized Core Chat Assistant Service powered by Google Gemini (google-genai SDK).
Implements fast prompt construction, token-efficient completions, and real-time streaming.
"""
import json
import logging
from typing import List, Dict, Any, Optional, Generator
from sqlalchemy.orm import Session
from google import genai
from google.genai import types

from app.core.config import settings
from app.services.chat_context_service import assemble_live_fleet_context
from app.services.chat_knowledge_base import RENTSENSE_APP_KNOWLEDGE_BASE

logger = logging.getLogger(__name__)


def build_system_prompt(live_context: str, knowledge_base: str) -> str:
    """
    Construct a concise, strictly grounded system instruction for Google Gemini.
    """
    return f"""You are the official RentSense Fleet Copilot, embedded in the RentSense Control Tower.
Answer questions accurately based on the provided live data and knowledge base.

[SECTION 1: LIVE FLEET DATA] (Authoritative for real-time fleet state)
{live_context}

[SECTION 2: GENERAL APP KNOWLEDGE] (Authoritative for how-tos and platform rules)
{knowledge_base}

[STRICT RULES]
1. GROUNDING: For questions about current machine state, alerts, or costs, strictly use SECTION 1. Never hallucinate or guess machine IDs, statuses, or metrics not in SECTION 1.
2. HOW-TOs: For status meanings, anomaly formulas, workflows, or forecasting math, use SECTION 2.
3. READ-ONLY: You cannot execute database mutations or check-outs. Provide UI navigation instructions when actions are requested.
4. STYLE: Be concise, clear, and operational. Use bold for equipment IDs (e.g. **EQX1001**) and bullet points for readability."""


def _get_gemini_client(api_key: Optional[str]) -> Optional[genai.Client]:
    if not api_key or not api_key.strip():
        return None
    return genai.Client(api_key=api_key.strip())


def _build_history_contents(
    message: str,
    history: Optional[List[Dict[str, str]]],
    max_turns: int = 4,
) -> List[types.Content]:
    contents: List[types.Content] = []
    if history:
        for h in history[-max_turns:]:
            role = "model" if h.get("role") in ("model", "assistant") else "user"
            text = h.get("content", "").strip()
            if text:
                contents.append(types.Content(role=role, parts=[types.Part.from_text(text=text)]))
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=message)]))
    return contents


def process_chat_message(
    db: Session,
    message: str,
    history: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """
    Non-streaming synchronous chat processing.
    """
    api_key = settings.GEMINI_API_KEY
    client = _get_gemini_client(api_key)
    if not client:
        return {
            "reply": "The AI assistant is not currently configured. Please set `GEMINI_API_KEY` in `.env` and restart the backend container to enable the RentSense fleet copilot.",
            "is_configured": False,
            "grounded": False,
            "model": settings.GEMINI_MODEL,
        }

    live_context = assemble_live_fleet_context(db, user_query=message)
    system_instruction = build_system_prompt(live_context, RENTSENSE_APP_KNOWLEDGE_BASE)
    contents = _build_history_contents(message, history, max_turns=settings.GEMINI_MAX_TURNS)
    model_name = settings.GEMINI_MODEL or "gemini-3.6-flash"

    try:
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2,
            max_output_tokens=450,
        )

        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=config,
        )

        reply_text = response.text or "No response generated. Please rephrase your question."
        return {
            "reply": reply_text,
            "is_configured": True,
            "grounded": True,
            "model": model_name,
        }
    except Exception as e:
        logger.error(f"[CHAT] Gemini API call error: {e}")
        return {
            "reply": "I encountered an issue contacting Google Gemini. The RentSense backend is operating normally, but the AI service is temporarily unavailable. Please try again in a moment.",
            "is_configured": True,
            "grounded": False,
            "model": model_name,
            "error": "Gemini API service communication failure.",
        }


def stream_chat_message(
    db: Session,
    message: str,
    history: Optional[List[Dict[str, str]]] = None,
) -> Generator[str, None, None]:
    """
    Streaming generator yielding Server-Sent Events (SSE) data chunks for fast perceived latency.
    """
    api_key = settings.GEMINI_API_KEY
    client = _get_gemini_client(api_key)
    model_name = settings.GEMINI_MODEL or "gemini-3.6-flash"

    if not client:
        payload = {
            "type": "error",
            "reply": "The AI assistant is not currently configured. Please set `GEMINI_API_KEY` in `.env` and restart the backend container.",
            "is_configured": False,
            "grounded": False,
        }
        yield f"data: {json.dumps(payload)}\n\n"
        return

    # 1. Yield stage notification
    yield f"data: {json.dumps({'type': 'stage', 'text': 'Analyzing fleet telemetry...'})}\n\n"

    try:
        live_context = assemble_live_fleet_context(db, user_query=message)
        system_instruction = build_system_prompt(live_context, RENTSENSE_APP_KNOWLEDGE_BASE)
        contents = _build_history_contents(message, history, max_turns=settings.GEMINI_MAX_TURNS)

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2,
            max_output_tokens=450,
        )

        # Call Gemini streaming
        response_stream = client.models.generate_content_stream(
            model=model_name,
            contents=contents,
            config=config,
        )

        for chunk in response_stream:
            text = ""
            try:
                if hasattr(chunk, "text") and chunk.text:
                    text = chunk.text
                elif chunk.candidates and len(chunk.candidates) > 0:
                    cand = chunk.candidates[0]
                    if cand.content and cand.content.parts:
                        for part in cand.content.parts:
                            if hasattr(part, "text") and part.text:
                                text += part.text
            except Exception:
                text = ""

            if text:
                yield f"data: {json.dumps({'type': 'chunk', 'text': text})}\n\n"

        # Signal completion
        yield f"data: {json.dumps({'type': 'done', 'is_configured': True, 'grounded': True, 'model': model_name})}\n\n"

    except Exception as e:
        logger.error(f"[CHAT] Gemini Streaming error: {e}")
        err_payload = {
            "type": "error",
            "reply": "I'm having trouble connecting to Google Gemini right now. Please try again in a moment.",
            "is_configured": True,
            "grounded": False,
        }
        yield f"data: {json.dumps(err_payload)}\n\n"
