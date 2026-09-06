from collections.abc import Sequence

from backend.rag.base import EmbeddingProvider, VectorStore
from backend.rag.models import DocumentChunk, RAGContext


def format_context(chunks) -> str:
    sections = []
    for chunk in chunks:
        citation = chunk.citation_id or chunk.source_id
        sections.append(
            f"[{citation}]\n"
            f"Title: {chunk.source_title}\n"
            f"URL: {chunk.source_url}\n"
            f"Relevance: {chunk.relevance_score:.3f}\n"
            f"Evidence:\n{chunk.content}"
        )
    return "\n\n".join(sections)


class SemanticRAGRetriever:
    def __init__(
        self,
        chunks: Sequence[DocumentChunk],
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
    ) -> None:
        self.chunks = list(chunks)
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        if self.chunks:
            embeddings = embedding_provider.embed_texts(
                [chunk.content for chunk in self.chunks]
            )
            vector_store.add(self.chunks, embeddings)

    def retrieve(self, question: str, top_k: int = 5) -> RAGContext:
        if not question.strip():
            raise ValueError("question cannot be blank")
        if top_k < 1:
            raise ValueError("top_k must be positive")
        if not self.chunks:
            return RAGContext(
                question=question,
                retrieved_chunks=[],
                context_text="",
                total_retrieved=0,
            )

        query_embedding = self.embedding_provider.embed_query(question)
        retrieved = self.vector_store.similarity_search(query_embedding, top_k)
        return RAGContext(
            question=question,
            retrieved_chunks=retrieved,
            context_text=format_context(retrieved),
            total_retrieved=len(retrieved),
        )