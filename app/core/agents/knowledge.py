import re
import logging
from typing import Dict, Any, Optional, List
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from tavily import TavilyClient
from app.core.agents.base import BaseAgent, AgentResponse
from app.services.vector_store import VectorStoreService
from app.config import settings
from app.utils.logging import sanitize_message_for_log, mask_user_key

logger = logging.getLogger(__name__)


KNOWLEDGE_PROMPT = """You are a helpful AI assistant for InfinitePay, a Brazilian payment processing company.

Use the provided context to answer the user's question accurately and concisely.

{history}

Context:
{context}

User question: {question}

Instructions:
- Answer in the same language as the question (Portuguese or English)
- Be concise and direct
- If the context contains relevant information to answer the question, USE IT to provide a helpful answer (even if not InfinitePay-related)
- If the context is empty or irrelevant, politely explain you don't have that information and offer to help with InfinitePay topics
- NEVER mention "context", "documents", "retrieved information", or other technical terms
- Speak naturally as a human assistant would
- When answering InfinitePay questions, focus on being accurate and helpful
- When answering general questions (weather, news, etc.), provide the information from the context if available
- Use conversation history ONLY if relevant to answer the current question (e.g., when user refers to previous topics)

Your answer:"""


class KnowledgeAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="knowledge")
        self.llm = ChatAnthropic(
            model=settings.ANTHROPIC_MODEL,
            api_key=settings.ANTHROPIC_API_KEY,
            temperature=0.3,
            max_tokens=1000
        )
        self.prompt = ChatPromptTemplate.from_template(KNOWLEDGE_PROMPT)
        self.chain = self.prompt | self.llm
        self.vector_store = VectorStoreService()
        self.tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)

    def _is_conversational(self, message: str) -> bool:
        message_without_metadata = re.sub(
            r'\[User\'?s?\s+real\s+first\s+name\s+is:.*?\]',
            '',
            message,
            flags=re.IGNORECASE | re.DOTALL
        ).strip()

        message_clean = re.sub(r'[^\w\s]', '', message_without_metadata.lower()).strip()

        greetings = [
            "oi", "olá", "ola", "hello", "hi", "hey",
            "bom dia", "boa tarde", "boa noite",
            "good morning", "good afternoon", "good evening"
        ]

        conversational_phrases = [
            "tudo bem", "tudo bom", "como vai", "como você está", "como vc está",
            "e aí", "e ai", "beleza", "tranquilo",
            "how are you", "how r u", "how are u", "how's it going", "how is it going",
            "what's up", "whats up", "wassup", "sup",
            "you good", "u good", "you ok", "u ok",
            "como está", "como esta", "tá bem", "ta bem"
        ]

        if message_clean in greetings:
            return True

        for phrase in conversational_phrases:
            if phrase in message_clean:
                return True

        if len(message_clean.split()) <= 4 and any(g in message_clean for g in greetings):
            return True

        return False

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
            self.logger.info(f"Searching web with Tavily: {sanitize_message_for_log(query, 100)}")
            response = self.tavily_client.search(
                query=query,
                max_results=3,
                search_depth=settings.TAVILY_SEARCH_DEPTH
            )

            if response and "results" in response:
                results = response["results"]
                self.logger.info(f"Tavily returned {len(results)} results")

                context_parts = []
                for idx, result in enumerate(results[:3], 1):
                    content = result.get('content', '')
                    context_parts.append(f"{idx}. {content}")
                    self.logger.info(f"Tavily result {idx}: {content[:150]}..." if len(content) > 150 else f"Tavily result {idx}: {content}")

                final_context = "\n\n".join(context_parts)
                self.logger.info(f"Tavily context total length: {len(final_context)} characters")
                self.logger.info(f"Tavily context preview: {final_context[:200]}...")
                return final_context
            else:
                self.logger.warning("Tavily returned no results or invalid response format")
                return "No relevant information found on the web."

        except Exception as e:
            self.logger.error(f"Tavily search error: {str(e)}")
            return f"Web search unavailable: {str(e)}"

    async def process(self, message: str, user_key: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        self.logger.info(f"Processing knowledge query for user {mask_user_key(user_key)}: {sanitize_message_for_log(message, 100)}")

        try:
            history_text = context.get("history", "") if context else ""

            context_text = ""
            source_type = "none"

            if self._is_conversational(message):
                self.logger.info("Detected conversational message, skipping web search (AI will respond naturally)")
                context_text = ""
                source_type = "conversational"
            else:
                route = context.get("route", "GENERAL") if context else "GENERAL"

                if route == "KNOWLEDGE":
                    self.logger.info("Router classified as KNOWLEDGE, using RAG")
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
                    self.logger.info("Router classified as GENERAL, using Tavily web search")
                    context_text = await self._search_with_tavily(message)
                    source_type = "tavily"

            result = await self.chain.ainvoke({
                "history": history_text,
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
