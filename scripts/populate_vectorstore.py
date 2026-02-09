import sys
import os

__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from app.utils.logging import setup_logging
from app.services.web_scraper import WebScraper
from app.services.text_chunker import TextChunker
from app.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)


def main():
    setup_logging("INFO")

    logger.info("=" * 60)
    logger.info("Starting RAG Pipeline: Populate Vector Store")
    logger.info("=" * 60)

    logger.info("Step 1: Scraping InfinitePay website...")
    scraper = WebScraper(timeout=30)
    pages = scraper.scrape_all()

    if not pages:
        logger.error("No pages scraped successfully. Exiting.")
        return

    logger.info(f"Successfully scraped {len(pages)} pages")
    for page in pages:
        logger.info(f"  - {page['url']}: {page['length']} chars")

    logger.info("\nStep 2: Chunking text...")
    chunker = TextChunker(chunk_size=500, overlap=50)
    all_chunks = []

    for page in pages:
        metadata = {
            "url": page["url"],
            "title": page["title"],
            "source": "infinitepay_website"
        }
        chunks = chunker.chunk_text(page["content"], metadata)
        all_chunks.extend(chunks)

    logger.info(f"Created {len(all_chunks)} chunks total")

    logger.info("\nStep 3: Populating vector store...")
    vector_store = VectorStoreService()

    existing_count = vector_store.count()
    if existing_count > 0:
        logger.warning(f"Vector store already contains {existing_count} documents")
        response = input("Clear existing data? (yes/no): ")
        if response.lower() == "yes":
            vector_store.clear()
            logger.info("Cleared existing data")
        else:
            logger.info("Keeping existing data, appending new documents")

    vector_store.add_documents(all_chunks)

    final_count = vector_store.count()
    logger.info(f"\n{'=' * 60}")
    logger.info(f"✅ RAG Pipeline Complete!")
    logger.info(f"📊 Total documents in vector store: {final_count}")
    logger.info(f"{'=' * 60}")

    logger.info("\nTesting retrieval...")
    test_query = "Como funciona o Pix?"
    results = vector_store.search(test_query, top_k=3)

    logger.info(f"\nTest Query: '{test_query}'")
    logger.info(f"Results: {len(results)} documents")
    for i, result in enumerate(results, 1):
        logger.info(f"\n  Result {i} (score: {result['score']:.3f}):")
        logger.info(f"  {result['text'][:200]}...")


if __name__ == "__main__":
    main()
