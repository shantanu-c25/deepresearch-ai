import hashlib

from backend.rag.loader import SourceDocument
from backend.rag.models import DocumentChunk


class DeterministicChunker:
    def __init__(self, max_chunk_size: int = 1000, overlap: int = 120) -> None:
        if max_chunk_size < 1:
            raise ValueError("max_chunk_size must be positive")
        if overlap < 0 or overlap >= max_chunk_size:
            raise ValueError("overlap must be between 0 and max_chunk_size")
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def chunk(self, document: SourceDocument) -> list[DocumentChunk]:
        text = document.content
        chunks: list[DocumentChunk] = []
        start = 0

        while start < len(text):
            end = min(start + self.max_chunk_size, len(text))
            if end < len(text):
                paragraph = text.rfind("\n", start, end)
                sentence = text.rfind(". ", start, end)
                word = text.rfind(" ", start, end)
                boundary = max(paragraph, sentence, word)
                if boundary > start:
                    end = boundary + (2 if boundary == sentence else 1)

            segment = text[start:end]
            content = segment.strip()
            content_start = start + len(segment) - len(segment.lstrip())
            content_end = content_start + len(content)
            if content:
                chunk_id = hashlib.sha256(
                    f"{document.source_id}:{content_start}:{content_end}:{content}".encode()
                ).hexdigest()[:16]
                chunks.append(
                    DocumentChunk(
                        id=f"{document.source_id}-chunk-{chunk_id}",
                        source_id=document.source_id,
                        citation_id=document.citation_id,
                        source_title=document.source_title,
                        source_url=document.source_url,
                        content=content,
                        chunk_index=len(chunks),
                        char_start=content_start,
                        char_end=content_end,
                        metadata=dict(document.metadata),
                    )
                )

            if end >= len(text):
                break
            candidate = max(end - self.overlap, start + 1)
            boundary_start = candidate
            while boundary_start > start and not text[boundary_start].isspace():
                boundary_start -= 1
            start = boundary_start if boundary_start > start else candidate

        return chunks
