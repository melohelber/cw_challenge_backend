import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class TextChunker:
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.separators = ["\n\n", "\n", ". ", "! ", "? ", ", ", " "]

    def chunk_text(self, text: str, metadata: Dict[str, str] = None) -> List[Dict[str, any]]:
        metadata = metadata or {}

        chunks = self._split_text(text)

        result = []
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) < 50:
                continue

            result.append({
                "text": chunk.strip(),
                "metadata": {
                    **metadata,
                    "chunk_id": i,
                    "total_chunks": len(chunks)
                }
            })

        logger.info(f"Chunked text into {len(result)} chunks (original: {len(text)} chars)")
        return result

    def _split_text(self, text: str) -> List[str]:
        if len(text) <= self.chunk_size:
            return [text]

        for separator in self.separators:
            if separator in text:
                parts = text.split(separator)
                chunks = []
                current_chunk = ""

                for part in parts:
                    if len(current_chunk) + len(part) + len(separator) <= self.chunk_size:
                        current_chunk += part + separator
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)

                        if len(part) > self.chunk_size:
                            sub_chunks = self._split_by_chars(part)
                            chunks.extend(sub_chunks[:-1])
                            current_chunk = sub_chunks[-1] if sub_chunks else ""
                        else:
                            current_chunk = part + separator

                if current_chunk:
                    chunks.append(current_chunk)

                if len(chunks) > 1:
                    return self._add_overlap(chunks)

        return self._split_by_chars(text)

    def _split_by_chars(self, text: str) -> List[str]:
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.overlap):
            chunk = text[i:i + self.chunk_size]
            if chunk.strip():
                chunks.append(chunk)
        return chunks

    def _add_overlap(self, chunks: List[str]) -> List[str]:
        if self.overlap == 0 or len(chunks) <= 1:
            return chunks

        overlapped = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_chunk = chunks[i - 1]
            current_chunk = chunks[i]

            overlap_text = prev_chunk[-self.overlap:] if len(prev_chunk) >= self.overlap else prev_chunk
            overlapped.append(overlap_text + current_chunk)

        return overlapped
