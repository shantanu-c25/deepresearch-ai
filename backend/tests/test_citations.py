from backend.models.source import ResearchSource
from backend.retrieval.citations import (
    build_citation_registry,
    extract_citation_ids,
    sanitize_invalid_citations,
    validate_citations,
)


def source(
    source_id: str,
    citation_id: str | None = None,
    title: str = "Source",
) -> ResearchSource:
    return ResearchSource(
        id=source_id,
        citation_id=citation_id,
        title=title,
        url=f"https://example.com/{source_id}",
        domain="example.com",
        provider="tavily",
        content="Evidence",
    )


def test_registry_is_deterministic_and_deduplicates_source_chunks():
    registry = build_citation_registry(
        [
            source("abc", "S1", "First chunk"),
            source("abc", "S1", "Second chunk"),
            source("def", None, "Second source"),
        ]
    )

    assert [entry.citation_id for entry in registry.entries] == ["S1", "S2"]
    assert [item.id for item in registry.sources] == ["abc", "def"]

    repeated = build_citation_registry(
        [
            source("abc", "S1", "First chunk"),
            source("abc", "S1", "Second chunk"),
            source("def", None, "Second source"),
        ]
    )
    assert repeated.model_dump() == registry.model_dump()


def test_registry_preserves_valid_ids_and_assigns_missing_ids_without_collisions():
    registry = build_citation_registry(
        [
            source("first", "S3"),
            source("second", None),
            source("third", "S3"),
        ]
    )

    assert [entry.citation_id for entry in registry.entries] == [
        "S3",
        "S1",
        "S2",
    ]
    assert registry.sources[0].citation_id == "S3"
    assert registry.sources[1].citation_id == "S1"
    assert registry.sources[2].citation_id == "S2"


def test_uploaded_source_gets_citation_without_losing_provenance():
    uploaded = ResearchSource(
        id="upload-blue-orchid",
        title="blue-orchid-test.txt",
        url="uploaded://upload-blue-orchid/blue-orchid-test.txt",
        domain="",
        source_type="documentation",
        provider="manual",
        content="The internal codename is BLUE ORCHID 742.",
    )

    registry = build_citation_registry([uploaded])

    assert registry.sources[0].citation_id == "S1"
    assert registry.sources[0].id == "upload-blue-orchid"
    assert registry.sources[0].url == uploaded.url
    assert registry.sources[0].title == "blue-orchid-test.txt"


def test_parser_extracts_supported_markers_and_ignores_other_brackets():
    text = "Fact [S1] and fact [S3]. [not a citation] [S0] [S01]"

    assert extract_citation_ids(text) == ["S1", "S3"]


def test_validator_rejects_unknown_ids_without_creating_sources():
    registry = build_citation_registry(
        [source("one"), source("two"), source("three")]
    )

    validation = validate_citations(
        "Fact A [S1]. Fact B [S99].",
        registry,
    )
    sanitized, _ = sanitize_invalid_citations(
        "Fact A [S1]. Fact B [S99].",
        registry,
    )

    assert validation.valid_ids == ["S1"]
    assert validation.invalid_ids == ["S99"]
    assert sanitized == "Fact A [S1]. Fact B."
    assert [source.citation_id for source in registry.sources] == [
        "S1",
        "S2",
        "S3",
    ]
