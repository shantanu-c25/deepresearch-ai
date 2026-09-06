from backend.models.source import (
    ResearchSource,
    SourceCollection,
)

from backend.validation.source_validator import (
    SourceValidator,
)


def test_government_source_is_high_credibility():
    source = ResearchSource(
        id="who-1",
        title=(
            "Artificial Intelligence "
            "for Health"
        ),
        url=(
            "https://www.who.int/"
            "health-topics/"
            "artificial-intelligence"
        ),
        domain="who.int",
        provider="tavily",
        source_type="report",
        relevance_score=0.9,
    )

    validated = (
        SourceValidator()
        .validate_source(source)
    )

    assert (
        validated.credibility
        == "high"
    )

    assert (
        validated.validation_status
        == "accepted"
    )


def test_arxiv_source_is_medium_credibility():
    source = ResearchSource(
        id="arxiv-1",
        title=(
            "Autonomous AI Agents "
            "in Healthcare"
        ),
        url=(
            "https://arxiv.org/"
            "abs/2603.17419"
        ),
        domain="arxiv.org",
        provider="arxiv",
        source_type="paper",
        relevance_score=0.8,
    )

    validated = (
        SourceValidator()
        .validate_source(source)
    )

    assert (
        validated.credibility
        == "medium"
    )

    assert (
        validated.validation_status
        == "accepted"
    )

    assert any(
        "preprint"
        in note.lower()
        for note
        in validated.validation_notes
    )


def test_vendor_source_is_medium_credibility():
    source = ResearchSource(
        id="vendor-1",
        title=(
            "AI Agents in Healthcare"
        ),
        url=(
            "https://www.ibm.com/"
            "think/topics/"
            "ai-agents-healthcare"
        ),
        domain="ibm.com",
        provider="tavily",
        relevance_score=0.8,
    )

    validated = (
        SourceValidator()
        .validate_source(source)
    )

    assert (
        validated.credibility
        == "medium"
    )

    assert (
        validated.validation_status
        == "accepted"
    )


def test_unknown_web_source_needs_review():
    source = ResearchSource(
        id="blog-1",
        title=(
            "AI Healthcare Blog"
        ),
        url=(
            "https://example-blog.com/"
            "ai-healthcare"
        ),
        domain="example-blog.com",
        provider="tavily",
        relevance_score=0.75,
    )

    validated = (
        SourceValidator()
        .validate_source(source)
    )

    assert (
        validated.credibility
        == "low"
    )

    assert (
        validated.validation_status
        == "needs-review"
    )


def test_low_relevance_source_is_rejected():
    source = ResearchSource(
        id="irrelevant-1",
        title=(
            "Agentic Literacy Debt"
        ),
        url=(
            "https://arxiv.org/"
            "abs/2605.27396"
        ),
        domain="arxiv.org",
        provider="arxiv",
        source_type="paper",
        relevance_score=0.15,
    )

    validated = (
        SourceValidator()
        .validate_source(source)
    )

    assert (
        validated.validation_status
        == "rejected"
    )


def test_relevant_quarter_score_source_is_kept():
    source = ResearchSource(
        id="relevant-1",
        title=(
            "Agentic AI Clinical "
            "Prediction"
        ),
        url=(
            "https://arxiv.org/"
            "abs/2602.19502"
        ),
        domain="arxiv.org",
        provider="arxiv",
        source_type="paper",
        relevance_score=0.25,
    )

    validated = (
        SourceValidator()
        .validate_source(source)
    )

    assert (
        validated.validation_status
        == "accepted"
    )


def test_collection_separates_all_statuses():
    accepted = ResearchSource(
        id="accepted-1",
        title=(
            "AI Agents in Healthcare"
        ),
        url=(
            "https://www.oracle.com/"
            "health/example"
        ),
        domain="oracle.com",
        provider="tavily",
        relevance_score=0.8,
    )

    review = ResearchSource(
        id="review-1",
        title=(
            "Healthcare AI Article"
        ),
        url=(
            "https://example-blog.com/"
            "healthcare-ai"
        ),
        domain="example-blog.com",
        provider="tavily",
        relevance_score=0.7,
    )

    rejected = ResearchSource(
        id="rejected-1",
        title=(
            "Unrelated AI Topic"
        ),
        url=(
            "https://arxiv.org/"
            "abs/1111.1111"
        ),
        domain="arxiv.org",
        provider="arxiv",
        relevance_score=0.1,
    )

    collection = SourceCollection(
        question=(
            "AI agents healthcare"
        ),
        sources=[
            accepted,
            review,
            rejected,
        ],
        total_found=3,
    )

    result = (
        SourceValidator()
        .validate_collection(
            collection
        )
    )

    assert (
        result.total_evaluated
        == 3
    )

    assert (
        len(
            result.accepted_sources
        )
        == 1
    )

    assert (
        len(
            result.review_sources
        )
        == 1
    )

    assert (
        len(
            result.rejected_sources
        )
        == 1
    )