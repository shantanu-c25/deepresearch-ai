import pytest

from backend.rag.chunker import DeterministicChunker
from backend.rag.loader import SourceDocument


def make_document(content: str) -> SourceDocument:
    return SourceDocument(
        source_id="source-1",
        citation_id="S1",
        source_title="A source",
        source_url="https://example.com/source",
        content=content,
        metadata={"provider": "tavily"},
    )


def test_short_document_is_one_chunk_with_provenance():
    chunks = DeterministicChunker(max_chunk_size=100, overlap=10).chunk(
        make_document("Short text.")
    )

    assert len(chunks) == 1
    assert chunks[0].content == "Short text."
    assert chunks[0].citation_id == "S1"
    assert chunks[0].char_start == 0
    assert chunks[0].char_end == len("Short text.")


def test_long_document_has_overlap_and_no_empty_chunks():
    chunks = DeterministicChunker(max_chunk_size=20, overlap=5).chunk(
        make_document("one two three four five six seven eight nine ten")
    )

    assert len(chunks) > 1
    assert all(chunk.content for chunk in chunks)
    assert any(
        first.content[-5:] in second.content
        for first, second in zip(chunks, chunks[1:])
    )


def test_chunk_ids_are_deterministic():
    document = make_document("A repeatable document with enough words to split.")
    first = DeterministicChunker(max_chunk_size=20, overlap=4).chunk(document)
    second = DeterministicChunker(max_chunk_size=20, overlap=4).chunk(document)

    assert [chunk.model_dump() for chunk in first] == [chunk.model_dump() for chunk in second]


@pytest.mark.parametrize(
    ("max_chunk_size", "overlap"),
    [(0, 0), (10, -1), (10, 10), (10, 11)],
)
def test_invalid_chunk_configuration_is_rejected(max_chunk_size, overlap):
    with pytest.raises(ValueError):
        DeterministicChunker(max_chunk_size=max_chunk_size, overlap=overlap)