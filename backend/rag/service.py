from backend.models.source import SourceCollection
from backend.rag.base import EmbeddingProvider, VectorStore
from backend.rag.chunker import DeterministicChunker
from backend.rag.embeddings import SentenceTransformerEmbeddingProvider
from backend.rag.loader import SourceDocumentLoader
from backend.rag.models import RAGContext
from backend.rag.semantic import SemanticRAGRetriever
from backend.rag.vector_store import InMemoryVectorStore
from backend.retrieval.evidence_formatter import prepare_evidence
from backend.retrieval.multi_source_retriever import MultiSourceRetriever
from backend.validation.source_validator import SourceValidator


class RAGPipelineService:
    def __init__(
        self,
        source_retriever=None,
        validator=None,
        document_loader=None,
        chunker=None,
        embedding_provider: EmbeddingProvider | None = None,
        vector_store_factory=InMemoryVectorStore,
    ) -> None:
        self.source_retriever = source_retriever or MultiSourceRetriever()
        self.validator = validator or SourceValidator()
        self.document_loader = document_loader or SourceDocumentLoader()
        self.chunker = chunker or DeterministicChunker()
        self.embedding_provider = embedding_provider or SentenceTransformerEmbeddingProvider()
        self.vector_store_factory = vector_store_factory

    def retrieve(self, question: str, top_k: int = 5) -> RAGContext:
        if not question.strip():
            raise ValueError("question cannot be blank")
        if top_k < 1:
            raise ValueError("top_k must be positive")

        collection = self.source_retriever.search(
            question,
            max_sources=max(top_k * 2, 8),
        )
        if not isinstance(collection, SourceCollection):
            raise TypeError("source retriever must return SourceCollection")
        validated = self.validator.validate_collection(collection)
        _, cited_sources = prepare_evidence(validated.accepted_sources)
        documents = self.document_loader.load_many(cited_sources)
        chunks = [chunk for document in documents for chunk in self.chunker.chunk(document)]
        semantic_retriever = SemanticRAGRetriever(
            chunks,
            self.embedding_provider,
            self.vector_store_factory(),
        )
        context = semantic_retriever.retrieve(question, top_k=top_k)
        return context.model_copy(
            update={
                "total_sources": len(cited_sources),
                "total_chunks": len(chunks),
            }
        )