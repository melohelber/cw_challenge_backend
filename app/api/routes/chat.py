import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_db, get_current_user_id
from app.models.schemas.chat import ChatRequest, ChatResponse
from app.core.orchestrator import AgentOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

orchestrator = AgentOrchestrator()


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_endpoint(
    request: ChatRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    logger.info(f"Chat request from user {current_user_id}: {request.message[:50]}...")

    try:
        result = await orchestrator.process_message(
            message=request.message,
            user_id=str(current_user_id),
            db=db
        )

        return ChatResponse(**result)

    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )
