import pytest
from pydantic import ValidationError

from backend.rag.models import DocumentChunk, RAGContext, RetrievedChunk


def chunk_data() -> dict:
    return {
        "id": "chunk-1",
        "source_id": "source-1",
        "citation_id": "S1",
        "source_title": "A source",
        "source_url": "https://example.com/source",
        "content": "Useful evidence.",
        "chunk_index": 0,
        "char_start": 0,
        "char_end": 16,
    }


def test_rag_models_have_expected_defaults():
    chunk = DocumentChunk(**chunk_data())
    retrieved = RetrievedChunk(**chunk_data(), relevance_score=0.8, rank=1)
    context = RAGContext(
        question="What happened?",
        retrieved_chunks=[retrieved],
        total_retrieved=1,
    )

    assert chunk.metadata == {}
    assert retrieved.rank == 1
    assert context.context_text == ""


@pytest.mark.parametrize("score", [-0.1, 1.1])
def test_retrieved_chunk_rejects_invalid_relevance(score):
    with pytest.raises(ValidationError):
        RetrievedChunk(**chunk_data(), relevance_score=score, rank=1)


def test_retrieved_chunk_rejects_invalid_rank():
    with pytest.raises(ValidationError):
        RetrievedChunk(**chunk_data(), relevance_score=0.5, rank=0)


def test_document_chunk_rejects_empty_content():
    with pytest.raises(ValidationError):
        DocumentChunk(**{**chunk_data(), "content": "   "})


def test_document_chunk_rejects_invalid_character_range():
    with pytest.raises(ValidationError):
        DocumentChunk(**{**chunk_data(), "char_start": 10, "char_end": 10})