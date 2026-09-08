from backend.models.source import SourceCollection
from backend.rag.base import EmbeddingProvider, VectorStore
from backend.rag.chunker import DeterministicChunker
from backend.rag.embeddings import SentenceTransformerEmbeddingProvider
from backend.rag.loader import SourceDocumentLoader
from backend.rag.models import RAGContext
from backend.rag.semantic import SemanticRAGRetriever, format_context
from backend.rag.vector_store import InMemoryVectorStore
from backend.rag.uploaded_loader import UploadedDocument
from backend.retrieval.evidence_formatter import prepare_evidence
from backend.retrieval.multi_source_retriever import MultiSourceRetriever
from backend.validation.source_validator import SourceValidator


_default_rag_pipeline_service: "RAGPipelineService | None" = None


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
        self.vector_store: VectorStore = self.vector_store_factory()
        self.uploaded_documents: list[UploadedDocument] = []
        self._indexed_chunk_ids: set[str] = set()

    def add_uploaded_document(self, uploaded: UploadedDocument) -> list:
        self.uploaded_documents.append(uploaded)
        chunks = self.chunker.chunk(uploaded.document)
        self._index_chunks(chunks)
        return chunks

    def _index_chunks(self, chunks: list) -> None:
        new_chunks = [chunk for chunk in chunks if chunk.id not in self._indexed_chunk_ids]
        if not new_chunks:
            return

        embeddings = self.embedding_provider.embed_texts(
            [chunk.content for chunk in new_chunks]
        )
        self.vector_store.add(new_chunks, embeddings)
        self._indexed_chunk_ids.update(chunk.id for chunk in new_chunks)

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
        documents.extend(uploaded.document for uploaded in self.uploaded_documents)
        chunks = [chunk for document in documents for chunk in self.chunker.chunk(document)]
        self._index_chunks(chunks)

        query_embedding = self.embedding_provider.embed_query(question)
        retrieved_chunks = self.vector_store.similarity_search(query_embedding, top_k)
        return RAGContext(
            question=question,
            retrieved_chunks=retrieved_chunks,
            context_text=format_context(retrieved_chunks),
            total_retrieved=len(retrieved_chunks),
            total_sources=len(cited_sources) + len(self.uploaded_documents),
            total_chunks=len(chunks),
        )


def get_rag_pipeline_service() -> RAGPipelineService:
    global _default_rag_pipeline_service

    if _default_rag_pipeline_service is None:
        _default_rag_pipeline_service = RAGPipelineService()

    return _default_rag_pipeline_service