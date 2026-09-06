from collections.abc import Sequence
from typing import Protocol

from backend.rag.models import DocumentChunk, RAGContext, RetrievedChunk


class DocumentChunker(Protocol):
    def chunk(self, document) -> list[DocumentChunk]:
        ...


class EmbeddingProvider(Protocol):
    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        ...

    def embed_query(self, query: str) -> list[float]:
        ...


class VectorStore(Protocol):
    def add(
        self,
        chunks: Sequence[DocumentChunk],
        embeddings: Sequence[Sequence[float]],
    ) -> None:
        ...

    def similarity_search(
        self,
        query_embedding: Sequence[float],
        limit: int,
    ) -> list[RetrievedChunk]:
        ...


class SemanticRetriever(Protocol):
    def retrieve(self, question: str, top_k: int = 5) -> RAGContext:
        ...