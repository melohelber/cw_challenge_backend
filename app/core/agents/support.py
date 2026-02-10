import logging
from typing import Dict, Any, Optional, List
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from langchain.tools import tool
from app.core.agents.base import BaseAgent, AgentResponse
from app.core.tools.user_lookup import user_lookup, get_user_info_description
from app.core.tools.transaction_history import transaction_history, get_transaction_history_description
from app.core.tools.account_status import account_status, get_account_status_description
from app.core.tools.transfer_troubleshoot import transfer_troubleshoot, get_transfer_troubleshoot_description
from app.config import settings
from app.utils.logging import sanitize_message_for_log, mask_user_key

logger = logging.getLogger(__name__)


SUPPORT_PROMPT = """You are a customer support agent for InfinitePay, a Brazilian payment processing company.

{history}

User Key: {user_key}
User question: {question}

You have access to the following tools to help the user:
- user_lookup: Get user profile information
- transaction_history: Get recent transactions
- account_status: Check account limits and restrictions
- transfer_troubleshoot: Diagnose transfer issues

Instructions:
- Answer in the same language as the question (Portuguese or English)
- Use the appropriate tools to gather information
- Be helpful, professional, and concise
- If you need a transfer_id from the user, ask for it
- Provide actionable recommendations when relevant
- DO NOT use the "name" field from tool results in your greetings (use generic greetings like "Olá!" instead)
- Focus on the technical information from tools, not personal data
- Use conversation history ONLY if relevant to answer the current question (e.g., when user refers to previous topics)

Your response:"""


class SupportAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="support")
        self.llm = ChatAnthropic(
            model=settings.ANTHROPIC_MODEL,
            api_key=settings.ANTHROPIC_API_KEY,
            temperature=0.3,
            max_tokens=1500
        )
        self.tools = self._create_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def _create_tools(self) -> List:
        @tool
        def lookup_user(user_key: str) -> Dict:
            """Get user profile information including name, email, account status, and verification level."""
            return user_lookup(user_key)

        @tool
        def get_transaction_history(user_key: str, limit: int = 5) -> Dict:
            """Get recent transaction history for a user. Limit specifies how many transactions to return (default 5)."""
            return transaction_history(user_key, limit)

        @tool
        def check_account_status(user_key: str) -> Dict:
            """Check account status, daily limits, and restrictions. Shows how much user can still transfer today."""
            return account_status(user_key)

        @tool
        def troubleshoot_transfer(transfer_id: str) -> Dict:
            """Diagnose transfer issues. Requires a transfer_id. Returns issue type, description, and recommendations."""
            return transfer_troubleshoot(transfer_id)

        return [lookup_user, get_transaction_history, check_account_status, troubleshoot_transfer]

    async def process(self, message: str, user_key: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        self.logger.info(f"Processing support request for user {mask_user_key(user_key)}: {sanitize_message_for_log(message, 100)}")

        try:
            # Extract conversation history from context
            history_text = context.get("history", "") if context else ""

            messages = [
                ("system", SUPPORT_PROMPT.format(history=history_text, user_key=user_key, question=message)),
                ("human", message)
            ]

            response = await self.llm_with_tools.ainvoke(messages)

            if response.tool_calls:
                self.logger.info(f"LLM requested {len(response.tool_calls)} tool calls")

                tool_results = []
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    self.logger.info(f"Calling tool: {tool_name} with args: {tool_args}")

                    tool_func = next((t for t in self.tools if t.name == tool_name), None)
                    if tool_func:
                        result = tool_func.invoke(tool_args)
                        tool_results.append({
                            "tool": tool_name,
                            "result": result
                        })

                second_response = await self.llm.ainvoke([
                    ("system", SUPPORT_PROMPT.format(history=history_text, user_key=user_key, question=message)),
                    ("human", f"Tool results:\n{tool_results}\n\nNow provide a helpful response to the user based on this information.")
                ])

                response_text = second_response.content.strip()

                return self._create_success_response(
                    response=response_text,
                    metadata={
                        "tools_used": [tc["name"] for tc in response.tool_calls],
                        "tool_count": len(response.tool_calls)
                    }
                )

            else:
                self.logger.info("No tools needed, responding directly")
                response_text = response.content.strip()

                return self._create_success_response(
                    response=response_text,
                    metadata={"tools_used": []}
                )

        except Exception as e:
            self.logger.error(f"Error processing support request: {str(e)}")
            return self._create_error_response(
                error=f"Failed to process support request: {str(e)}"
            )
