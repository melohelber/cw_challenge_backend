import sys
import os

__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.vector_store import VectorStoreService

def main():
    vs = VectorStoreService()

    print('=' * 60)
    print('RAG DATABASE - InfinitePay Knowledge Base')
    print('=' * 60)
    print(f'Total chunks: {vs.count()}')
    print(f'Collection: {vs.collection_name}')
    print()

    collection = vs.collection
    sample_data = collection.get(limit=5, include=['documents', 'metadatas'])

    print('Sample chunks from different pages:')
    print('=' * 60)

    for i, (doc, meta) in enumerate(zip(sample_data['documents'], sample_data['metadatas']), 1):
        print(f'\n[Chunk #{i}]')
        print(f'Source: {meta.get("url", "unknown")}')
        print(f'Title: {meta.get("title", "unknown")[:50]}...')
        print(f'Content preview:')
        print(f'  {doc[:200].replace(chr(10), " ")}...')
        print('-' * 60)

if __name__ == "__main__":
    main()
