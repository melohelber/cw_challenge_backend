import logging
from typing import Dict, Any, Optional, List
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from tavily import TavilyClient
from app.core.agents.base import BaseAgent, AgentResponse
from app.services.vector_store import VectorStoreService
from app.config import settings

logger = logging.getLogger(__name__)


KNOWLEDGE_PROMPT = """You are a helpful assistant for InfinitePay, a Brazilian payment processing company.

Use the provided context to answer the user's question accurately and concisely.

Context:
{context}

User question: {question}

Instructions:
- Answer in the same language as the question (Portuguese or English)
- Be concise and direct
- If the context doesn't contain relevant information, say so
- Focus on InfinitePay products and services when applicable

Your answer:"""


class KnowledgeAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="knowledge")
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=settings.ANTHROPIC_API_KEY,
            temperature=0.3,
            max_tokens=1000
        )
        self.prompt = ChatPromptTemplate.from_template(KNOWLEDGE_PROMPT)
        self.chain = self.prompt | self.llm
        self.vector_store = VectorStoreService()
        self.tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)

    def _is_infinitepay_related(self, message: str) -> bool:
        infinitepay_keywords = [
            "infinitepay", "maquininha", "pix", "pagamento", "payment",
            "tap to pay", "pdv", "taxa", "fee", "cartão", "card",
            "transferência", "transfer", "credenciadora", "adquirente"
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in infinitepay_keywords)

    async def _search_with_rag(self, query: str, top_k: int = 3) -> List[str]:
        try:
            results = self.vector_store.search(query, top_k=top_k)
            if results:
                self.logger.info(f"RAG found {len(results)} relevant documents")
                return [doc["text"] for doc in results]
            return []
        except Exception as e:
            self.logger.error(f"RAG search error: {str(e)}")
            return []

    async def _search_with_tavily(self, query: str) -> str:
        try:
            self.logger.info(f"Searching web with Tavily: {query}")
            response = self.tavily_client.search(
                query=query,
                max_results=3,
                search_depth="basic"
            )

            if response and "results" in response:
                results = response["results"]
                context_parts = []
                for idx, result in enumerate(results[:3], 1):
                    context_parts.append(f"{idx}. {result.get('content', '')}")
                return "\n\n".join(context_parts)
            return "No relevant information found on the web."

        except Exception as e:
            self.logger.error(f"Tavily search error: {str(e)}")
            return f"Web search unavailable: {str(e)}"

    async def process(self, message: str, user_id: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        self.logger.info(f"Processing knowledge query for user {user_id}: {message[:100]}...")

        try:
            context_text = ""
            source_type = "none"

            if self._is_infinitepay_related(message):
                self.logger.info("InfinitePay-related question, using RAG")
                documents = await self._search_with_rag(message, top_k=3)

                if documents:
                    context_text = "\n\n".join(documents)
                    source_type = "rag"
                    self.logger.info("Using RAG context")
                else:
                    self.logger.info("No RAG results, falling back to Tavily")
                    context_text = await self._search_with_tavily(message)
                    source_type = "tavily_fallback"
            else:
                self.logger.info("General question, using Tavily web search")
                context_text = await self._search_with_tavily(message)
                source_type = "tavily"

            result = await self.chain.ainvoke({
                "context": context_text,
                "question": message
            })

            response_text = result.content.strip()

            return self._create_success_response(
                response=response_text,
                metadata={
                    "source_type": source_type,
                    "context_length": len(context_text)
                }
            )

        except Exception as e:
            self.logger.error(f"Error processing knowledge query: {str(e)}")
            return self._create_error_response(
                error=f"Failed to process query: {str(e)}"
            )
