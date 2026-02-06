import logging
from typing import List, Dict, Optional
import chromadb
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self, collection_name: str = "infinitepay_knowledge"):
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(path="./data/vectorstore")

        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        try:
            self.collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"Loaded existing collection: {collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function,
                metadata={"description": "InfinitePay knowledge base for RAG"}
            )
            logger.info(f"Created new collection: {collection_name}")

    def add_documents(self, documents: List[Dict[str, any]]) -> None:
        if not documents:
            logger.warning("No documents to add")
            return

        ids = [f"doc_{i}" for i in range(len(documents))]
        texts = [doc["text"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]

        logger.info(f"Adding {len(documents)} documents to vector store...")

        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )

        logger.info(f"Successfully added {len(documents)} documents")

    def search(self, query: str, top_k: int = 5, min_score: float = 0.0) -> List[Dict[str, any]]:
        logger.info(f"Searching vector store: '{query[:50]}...' (top_k={top_k})")

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )

        documents = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                distance = results["distances"][0][i] if results.get("distances") else 0
                score = 1 - distance

                if score >= min_score:
                    metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                    documents.append({
                        "text": doc,
                        "score": score,
                        "metadata": metadata
                    })

        logger.info(f"Found {len(documents)} relevant documents (score >= {min_score})")
        return documents

    def count(self) -> int:
        return self.collection.count()

    def clear(self) -> None:
        logger.warning(f"Clearing collection: {self.collection_name}")
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function
        )
        logger.info("Collection cleared")

    def get_all_documents(self) -> List[Dict[str, any]]:
        count = self.count()
        if count == 0:
            return []

        results = self.collection.get()

        documents = []
        for i in range(len(results["ids"])):
            documents.append({
                "id": results["ids"][i],
                "text": results["documents"][i],
                "metadata": results["metadatas"][i] if results.get("metadatas") else {}
            })

        return documents
