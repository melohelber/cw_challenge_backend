import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_db, get_current_user_key
from app.models.schemas.chat import ChatRequest, ChatResponse
from app.core.orchestrator import AgentOrchestrator
from app.utils.logging import sanitize_message_for_log, mask_user_key

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

orchestrator = AgentOrchestrator()


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_endpoint(
    request: ChatRequest,
    current_user_key: str = Depends(get_current_user_key),
    db: Session = Depends(get_db)
):
    logger.info(f"Chat request from user {mask_user_key(current_user_key)}: {sanitize_message_for_log(request.message, 50)}")

    try:
        result = await orchestrator.process_message(
            message=request.message,
            user_key=current_user_key,
            db=db
        )

        logger.info(
            f"Response sent | user_key={mask_user_key(current_user_key)} | "
            f"agent_used={result['agent_used']} | "
            f"confidence={result.get('confidence')} | "
            f"response_length={len(result['response'])}"
        )

        return ChatResponse(
            response=result["response"],
            agent_used=result.get("agent_used")
        )

    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )
