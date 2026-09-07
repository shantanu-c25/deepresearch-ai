from typing import Any, Protocol, runtime_checkable

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import Runnable, RunnableLambda
from pydantic import ConfigDict, Field

from backend.rag.models import DocumentChunk, RAGContext


@runtime_checkable
class RAGServiceProtocol(Protocol):
    def retrieve(self, question: str, top_k: int = 5) -> RAGContext:
        ...


def chunk_to_langchain_document(chunk: DocumentChunk) -> Document:
    """Convert a canonical RAG chunk without dropping provenance."""
    metadata: dict[str, Any] = dict(chunk.metadata)
    metadata.update(
        {
            "chunk_id": chunk.id,
            "source_id": chunk.source_id,
            "citation_id": chunk.citation_id,
            "source_title": chunk.source_title,
            "source_url": chunk.source_url,
            "chunk_index": chunk.chunk_index,
            "char_start": chunk.char_start,
            "char_end": chunk.char_end,
        }
    )
    if hasattr(chunk, "relevance_score"):
        metadata["relevance_score"] = getattr(chunk, "relevance_score")
    if hasattr(chunk, "rank"):
        metadata["rank"] = getattr(chunk, "rank")
    return Document(page_content=chunk.content, metadata=metadata)


def _document_context(document: Document) -> str:
    metadata = document.metadata
    citation = metadata.get("citation_id") or metadata["source_id"]
    return (
        f"[{citation}]\n"
        f"Title: {metadata['source_title']}\n"
        f"URL: {metadata['source_url']}\n"
        f"Relevance: {float(metadata.get('relevance_score', 0.0)):.3f}\n"
        f"Evidence:\n{document.page_content}"
    )


def langchain_documents_to_context(documents: list[Document]) -> str:
    """Keep the existing semantic context shape for downstream agents."""
    return "\n\n".join(_document_context(document) for document in documents)


class RAGPipelineRetriever(BaseRetriever):
    """LangChain retriever facade backed by the existing RAG pipeline."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    rag_service: RAGServiceProtocol = Field(exclude=True)
    top_k: int = 5

    def _get_relevant_documents(self, query: str, *, run_manager) -> list[Document]:
        context: RAGContext = self.rag_service.retrieve(query, top_k=self.top_k)
        return [chunk_to_langchain_document(chunk) for chunk in context.retrieved_chunks]


def build_retrieval_context_chain(
    retriever: RAGPipelineRetriever,
) -> Runnable[str, dict[str, Any]]:
    """Compose one existing RAG retrieval with LangChain context formatting."""

    def retrieve_and_format(question: str) -> dict[str, Any]:
        documents = retriever.invoke(question)
        return {
            "question": question,
            "documents": documents,
            "context_text": langchain_documents_to_context(documents),
        }

    return RunnableLambda(retrieve_and_format)