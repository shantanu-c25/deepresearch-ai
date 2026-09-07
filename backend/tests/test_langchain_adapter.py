from backend.rag.langchain_adapter import (
    RAGPipelineRetriever,
    build_retrieval_context_chain,
    chunk_to_langchain_document,
    langchain_documents_to_context,
)
from backend.rag.models import DocumentChunk, RAGContext, RetrievedChunk


def make_chunk(**updates):
    data = {
        "id": "chunk-1",
        "source_id": "source-1",
        "citation_id": "S1",
        "source_title": "Research source",
        "source_url": "https://example.com/source",
        "content": "Useful evidence.",
        "chunk_index": 2,
        "char_start": 10,
        "char_end": 27,
        "metadata": {
            "provider": "tavily",
            "source_type": "web",
            "domain": "example.com",
        },
    }
    data.update(updates)
    return DocumentChunk(**data)


def test_chunk_conversion_preserves_tavily_provenance():
    document = chunk_to_langchain_document(make_chunk())

    assert document.page_content == "Useful evidence."
    assert document.metadata["chunk_id"] == "chunk-1"
    assert document.metadata["source_id"] == "source-1"
    assert document.metadata["citation_id"] == "S1"
    assert document.metadata["provider"] == "tavily"
    assert document.metadata["source_type"] == "web"
    assert document.metadata["chunk_index"] == 2
    assert document.metadata["char_start"] == 10
    assert document.metadata["char_end"] == 27


def test_chunk_conversion_preserves_arxiv_and_uploaded_metadata():
    arxiv = chunk_to_langchain_document(
        make_chunk(
            metadata={
                "provider": "arxiv",
                "source_type": "paper",
                "authors": ["Author"],
            }
        )
    )
    uploaded = chunk_to_langchain_document(
        make_chunk(
            source_id="upload-1",
            citation_id=None,
            source_title="notes.txt",
            source_url="uploaded://upload-1/notes.txt",
            metadata={
                "source_type": "uploaded_document",
                "filename": "notes.txt",
                "file_extension": ".txt",
                "mime_type": "text/plain",
            },
        )
    )

    assert arxiv.metadata["provider"] == "arxiv"
    assert arxiv.metadata["source_type"] == "paper"
    assert arxiv.metadata["authors"] == ["Author"]
    assert uploaded.metadata["source_type"] == "uploaded_document"
    assert uploaded.metadata["filename"] == "notes.txt"
    assert uploaded.metadata["file_extension"] == ".txt"
    assert uploaded.metadata["mime_type"] == "text/plain"
    assert uploaded.metadata["source_url"] == "uploaded://upload-1/notes.txt"


class FakeRAGService:
    def __init__(self, context):
        self.context = context
        self.calls = []

    def retrieve(self, question, top_k):
        self.calls.append((question, top_k))
        return self.context


def test_retriever_delegates_once_and_does_not_create_embeddings_or_a_store():
    retrieved = RetrievedChunk(
        **make_chunk().model_dump(),
        relevance_score=0.875,
        rank=1,
    )
    service = FakeRAGService(
        RAGContext(
            question="question",
            retrieved_chunks=[retrieved],
            total_retrieved=1,
        )
    )
    retriever = RAGPipelineRetriever(rag_service=service, top_k=3)

    documents = retriever.invoke("question")

    assert service.calls == [("question", 3)]
    assert len(documents) == 1
    assert documents[0].page_content == "Useful evidence."
    assert documents[0].metadata["relevance_score"] == 0.875
    assert documents[0].metadata["rank"] == 1


def test_context_chain_formats_documents_and_handles_empty_retrieval():
    service = FakeRAGService(
        RAGContext(
            question="question",
            retrieved_chunks=[],
            total_retrieved=0,
        )
    )
    chain = build_retrieval_context_chain(
        RAGPipelineRetriever(rag_service=service, top_k=2)
    )

    result = chain.invoke("question")

    assert result["question"] == "question"
    assert result["documents"] == []
    assert result["context_text"] == ""


def test_context_formatter_matches_existing_evidence_shape():
    document = chunk_to_langchain_document(
        RetrievedChunk(
            **make_chunk().model_dump(),
            relevance_score=0.5,
            rank=1,
        )
    )

    context = langchain_documents_to_context([document])

    assert "[S1]" in context
    assert "Title: Research source" in context
    assert "URL: https://example.com/source" in context
    assert "Relevance: 0.500" in context
    assert "Evidence:\nUseful evidence." in context