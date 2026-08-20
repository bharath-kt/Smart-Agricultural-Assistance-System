"""Chatbot API router endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.user import User
from app.core.security import get_optional_current_user
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chatbot_service import chatbot_service
from app.core.logging import get_logger

router = APIRouter(prefix="/chat", tags=["Chatbot Assistant"])
logger = get_logger(__name__)


@router.post("", response_model=ChatResponse)
@router.post("/", response_model=ChatResponse, include_in_schema=False)
async def chat_with_assistant(
    request: ChatRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Process natural language agricultural questions with AI assistant."""
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty."
        )

    try:
        history_list = [msg.model_dump() for msg in (request.conversation_history or [])]
        result = await chatbot_service.process_chat(
            message=request.message,
            language=request.language or "en",
            history=history_list,
            user_profile=current_user,
            db=db
        )

        return ChatResponse(
            response=result["response"],
            intent=result["intent"],
            language=result["language"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chatbot endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your message."
        )
