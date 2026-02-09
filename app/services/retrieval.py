import logging
from typing import List, Dict, Optional
from app.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)


class RetrievalService:
    def __init__(self, vector_store: Optional[VectorStoreService] = None):
        self.vector_store = vector_store or VectorStoreService()

    def retrieve(self, query: str, top_k: int = 5, min_score: float = 0.5) -> Dict[str, any]:
        logger.info(f"Retrieving documents for query: '{query[:50]}...'")

        documents = self.vector_store.search(query, top_k=top_k, min_score=min_score)

        if not documents:
            logger.warning(f"No relevant documents found for query")
            return {
                "query": query,
                "documents": [],
                "context": "",
                "sources": []
            }

        context = self._build_context(documents)
        sources = self._extract_sources(documents)

        logger.info(f"Retrieved {len(documents)} documents, context length: {len(context)} chars")

        return {
            "query": query,
            "documents": documents,
            "context": context,
            "sources": sources,
            "num_results": len(documents)
        }

    def _build_context(self, documents: List[Dict[str, any]]) -> str:
        context_parts = []

        for i, doc in enumerate(documents, 1):
            score = doc.get("score", 0)
            text = doc.get("text", "")
            metadata = doc.get("metadata", {})
            url = metadata.get("url", "")

            context_parts.append(f"[Document {i}] (relevance: {score:.2f})")
            if url:
                context_parts.append(f"Source: {url}")
            context_parts.append(text)
            context_parts.append("")

        return "\n".join(context_parts)

    def _extract_sources(self, documents: List[Dict[str, any]]) -> List[str]:
        sources = set()

        for doc in documents:
            metadata = doc.get("metadata", {})
            url = metadata.get("url")
            if url:
                sources.add(url)

        return list(sources)

    def check_health(self) -> Dict[str, any]:
        try:
            count = self.vector_store.count()
            return {
                "status": "healthy" if count > 0 else "empty",
                "document_count": count
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
