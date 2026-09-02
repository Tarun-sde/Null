from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class ChatMessageHistory(BaseModel):
    role: str = Field(..., description="'user' or 'assistant' / 'model'")
    content: str = Field(..., description="Text content of the message")


class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User's natural language question")
    history: Optional[List[ChatMessageHistory]] = Field(default=None, description="Recent conversation turns (capped for context)")


class ChatMessageResponse(BaseModel):
    reply: str
    is_configured: bool = True
    grounded: bool = True
    model: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
