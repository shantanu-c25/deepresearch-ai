import pytest
from pydantic import ValidationError

from backend.models.source import (
    ResearchSource,
    SourceCollection,
)


def test_research_source_can_be_created():
    source = ResearchSource(
        id="arxiv-test-1",
        title="AI Agents in Healthcare",
        url=(
            "https://arxiv.org/"
            "abs/2609.00001"
        ),
        domain="arxiv.org",
        source_type="paper",
        provider="arxiv",
        authors=[
            "Researcher One",
            "Researcher Two",
        ],
        relevance_score=0.91,
        credibility="high",
    )

    assert source.title == (
        "AI Agents in Healthcare"
    )

    assert source.provider == "arxiv"

    assert source.source_type == "paper"

    assert source.relevance_score == 0.91

    assert len(source.authors) == 2


def test_source_defaults_are_safe():
    source = ResearchSource(
        id="web-test-1",
        title="AI Healthcare Overview",
        url="https://example.com/article",
        domain="example.com",
        provider="tavily",
    )

    assert source.snippet == ""

    assert source.content == ""

    assert source.authors == []

    assert source.credibility == "unrated"

    assert source.relevance_score == 0.0


def test_relevance_score_cannot_exceed_one():
    with pytest.raises(
        ValidationError
    ):
        ResearchSource(
            id="invalid-score",
            title="Invalid Source",
            url="https://example.com",
            domain="example.com",
            provider="tavily",
            relevance_score=1.5,
        )


def test_source_collection():
    source = ResearchSource(
        id="source-1",
        title="Example Research",
        url="https://example.com",
        domain="example.com",
        provider="tavily",
    )

    collection = SourceCollection(
        question=(
            "How are AI agents used "
            "in healthcare?"
        ),
        sources=[source],
        total_found=1,
    )

    assert collection.total_found == 1

    assert len(collection.sources) == 1

    assert (
        collection.sources[0].id
        == "source-1"
    )