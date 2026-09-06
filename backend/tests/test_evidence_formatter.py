from backend.models.source import (
    ResearchSource,
)

from backend.retrieval.evidence_formatter import (
    prepare_evidence,
)


def test_prepare_evidence_assigns_citation_ids():
    sources = [
        ResearchSource(
            id="source-a",
            title="Healthcare AI",
            url=(
                "https://example.com/a"
            ),
            domain="example.com",
            provider="tavily",
            relevance_score=0.8,
            credibility="medium",
            validation_status="accepted",
            content=(
                "Healthcare AI evidence."
            ),
        ),
        ResearchSource(
            id="source-b",
            title=(
                "Agentic Healthcare"
            ),
            url=(
                "https://arxiv.org/"
                "abs/2601.00001"
            ),
            domain="arxiv.org",
            provider="arxiv",
            source_type="paper",
            relevance_score=0.7,
            credibility="medium",
            validation_status="accepted",
            content=(
                "Academic evidence."
            ),
        ),
    ]

    context, prepared = (
        prepare_evidence(
            sources
        )
    )

    assert (
        prepared[0].citation_id
        == "S1"
    )

    assert (
        prepared[1].citation_id
        == "S2"
    )

    assert "[S1]" in context

    assert "[S2]" in context


def test_prepare_evidence_preserves_original_sources():
    source = ResearchSource(
        id="source-a",
        title="Healthcare AI",
        url="https://example.com/a",
        domain="example.com",
        provider="tavily",
        relevance_score=0.8,
        credibility="medium",
        validation_status="accepted",
    )

    _, prepared = prepare_evidence(
        [source]
    )

    assert source.citation_id is None

    assert (
        prepared[0].citation_id
        == "S1"
    )


def test_prepare_evidence_truncates_long_content():
    source = ResearchSource(
        id="source-a",
        title="Healthcare AI",
        url="https://example.com/a",
        domain="example.com",
        provider="tavily",
        relevance_score=0.8,
        credibility="medium",
        validation_status="accepted",
        content="A" * 500,
    )

    context, _ = prepare_evidence(
        [source],
        max_chars_per_source=100,
    )

    assert (
        ("A" * 100) + "..."
        in context
    )

    assert (
        "A" * 101
        not in context
    )


def test_prepare_evidence_handles_empty_sources():
    context, prepared = (
        prepare_evidence([])
    )

    assert context == ""

    assert prepared == []