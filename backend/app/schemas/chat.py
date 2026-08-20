"""Chatbot API Pydantic schemas."""
from typing import Optional, List
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Individual message in conversation history."""
    sender: str = Field(..., description="Message sender ('user' or 'bot')")
    text: str = Field(..., description="Message text content")
    timestamp: Optional[str] = Field(None, description="Optional timestamp string")


class ChatRequest(BaseModel):
    """Chatbot request schema."""
    message: str = Field(..., description="User question or input text")
    language: Optional[str] = Field("en", description="Preferred language ('en' or 'kn')")
    conversation_history: Optional[List[ChatMessage]] = Field(
        default_factory=list, description="Recent conversation turns"
    )


class ChatResponse(BaseModel):
    """Chatbot response schema."""
    response: str = Field(..., description="Assistant response text")
    intent: str = Field(..., description="Detected intent key")
    language: str = Field("en", description="Response language")
