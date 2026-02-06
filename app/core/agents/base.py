import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class AgentResponse:
    success: bool
    response: str
    agent_name: str
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"agent.{name}")

    @abstractmethod
    async def process(self, message: str, user_id: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        raise NotImplementedError("Subclasses must implement process() method")

    def _create_success_response(self, response: str, metadata: Optional[Dict[str, Any]] = None) -> AgentResponse:
        return AgentResponse(
            success=True,
            response=response,
            agent_name=self.name,
            metadata=metadata or {}
        )

    def _create_error_response(self, error: str, metadata: Optional[Dict[str, Any]] = None) -> AgentResponse:
        return AgentResponse(
            success=False,
            response="",
            agent_name=self.name,
            error=error,
            metadata=metadata or {}
        )
