from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User message")


class ChatResponse(BaseModel):
    response: str = Field(..., description="Agent response")
    agent_used: str = Field(..., description="Which agent processed the message")
    confidence: Optional[float] = Field(None, description="Routing confidence score")
    metadata: Optional[dict] = Field(default_factory=dict, description="Additional metadata")
