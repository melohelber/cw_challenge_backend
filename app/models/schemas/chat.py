from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User message")


class ChatResponse(BaseModel):
    response: str = Field(..., description="Agent response")
    agent_used: Optional[str] = Field(None, description="Agent that processed the message")
    confidence: Optional[str] = Field(None, description="Router confidence level")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
