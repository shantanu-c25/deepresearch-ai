from datetime import (
    datetime,
    timezone,
)

from backend.retrieval.arxiv_retriever import (
    ArxivRetriever,
)


class FakeAuthor:
    def __init__(
        self,
        name: str,
    ):
        self.name = name


class FakeArxivResult:
    title = (
        "  AI Agents in "
        "Healthcare  "
    )

    entry_id = (
        "https://arxiv.org/"
        "abs/2609.12345"
    )

    summary = (
        "AI agents can support\n"
        "clinical workflows and "
        "decision making."
    )

    authors = [
        FakeAuthor(
            "Researcher One"
        ),
        FakeAuthor(
            "Researcher Two"
        ),
    ]

    published = datetime(
        2026,
        9,
        1,
        tzinfo=timezone.utc,
    )


class FakeArxivClient:
    def __init__(self):
        self.last_search = None


    def results(
        self,
        search,
    ):
        self.last_search = search

        return iter(
            [
                FakeArxivResult()
            ]
        )


def test_arxiv_retriever_normalizes_papers():
    client = FakeArxivClient()

    retriever = ArxivRetriever(
        client=client
    )

    sources = retriever.search(
        "AI agents healthcare",
        max_results=3,
    )

    assert len(sources) == 1

    source = sources[0]

    assert (
        source.provider
        == "arxiv"
    )

    assert (
        source.source_type
        == "paper"
    )

    assert (
        source.domain
        == "arxiv.org"
    )

    assert (
        source.title
        == "AI Agents in Healthcare"
    )

    assert source.authors == [
        "Researcher One",
        "Researcher Two",
    ]

    assert (
        source.published_date
        == "2026-09-01"
    )

    assert (
        source.credibility
        == "medium"
    )


def test_arxiv_retriever_cleans_summary():
    client = FakeArxivClient()

    retriever = ArxivRetriever(
        client=client
    )

    sources = retriever.search(
        "AI healthcare"
    )

    assert (
        sources[0].snippet
        == (
            "AI agents can support "
            "clinical workflows and "
            "decision making."
        )
    )

    assert (
        sources[0].content
        == sources[0].snippet
    )


def test_arxiv_empty_question_returns_no_sources():
    client = FakeArxivClient()

    retriever = ArxivRetriever(
        client=client
    )

    sources = retriever.search(
        "   "
    )

    assert sources == []

    assert (
        client.last_search
        is None
    )


def test_arxiv_retriever_uses_optimized_query():
    client = FakeArxivClient()

    retriever = ArxivRetriever(
        client=client
    )

    retriever.search(
        (
            "What are the main "
            "benefits and risks "
            "of AI agents in "
            "healthcare?"
        )
    )

    assert (
        client.last_search.query
        == (
            "all:ai AND "
            "all:agents AND "
            "all:healthcare"
        )
    )