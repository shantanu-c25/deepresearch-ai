from backend.models.source import ResearchSource
from backend.rag.loader import SourceDocumentLoader


def make_source(**updates):
    data = {
        "id": "source-1",
        "citation_id": "S1",
        "title": "A source",
        "url": "https://example.com/source",
        "domain": "example.com",
        "provider": "tavily",
        "content": "Loaded content",
        "snippet": "Snippet fallback",
    }
    data.update(updates)
    return ResearchSource(**data)


def test_content_is_preferred_over_snippet():
    document = SourceDocumentLoader().load(make_source())

    assert document is not None
    assert document.content == "Loaded content"


def test_snippet_is_used_as_fallback():
    document = SourceDocumentLoader().load(make_source(content=""))

    assert document is not None
    assert document.content == "Snippet fallback"


def test_whitespace_is_normalized_and_provenance_preserved():
    document = SourceDocumentLoader().load(
        make_source(content=" first\n\nsecond\tthird ")
    )

    assert document is not None
    assert document.content == "first second third"
    assert document.source_id == "source-1"
    assert document.citation_id == "S1"
    assert document.source_title == "A source"
    assert document.source_url == "https://example.com/source"
    assert document.metadata["provider"] == "tavily"


def test_empty_source_is_explicitly_skipped():
    assert SourceDocumentLoader().load(make_source(content="", snippet="")) is None


def test_multiple_sources_are_loaded_without_inventing_content():
    sources = [make_source(id="one"), make_source(id="two", content="", snippet="")]

    documents = SourceDocumentLoader().load_many(sources)

    assert [document.source_id for document in documents] == ["one"]