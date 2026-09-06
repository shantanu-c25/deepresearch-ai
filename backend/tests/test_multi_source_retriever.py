from backend.models.source import (
    ResearchSource,
)

from backend.retrieval.multi_source_retriever import (
    MultiSourceRetriever,
)


class FakeRetriever:
    def __init__(
        self,
        sources,
    ):
        self.sources = sources

        self.last_question = None

        self.last_max_results = None


    def search(
        self,
        question,
        max_results=5,
    ):
        self.last_question = (
            question
        )

        self.last_max_results = (
            max_results
        )

        return self.sources


def test_multi_source_retriever_combines_sources():
    tavily_source = ResearchSource(
        id="web-1",
        title=(
            "AI Agents in Healthcare"
        ),
        url=(
            "https://example.com/"
            "healthcare-agents"
        ),
        domain="example.com",
        source_type="web",
        provider="tavily",
        snippet=(
            "AI agents support "
            "healthcare workflows."
        ),
        relevance_score=0.9,
    )

    arxiv_source = ResearchSource(
        id="paper-1",
        title=(
            "Clinical AI Agents "
            "for Healthcare"
        ),
        url=(
            "https://arxiv.org/"
            "abs/2601.00001"
        ),
        domain="arxiv.org",
        source_type="paper",
        provider="arxiv",
        snippet=(
            "Clinical AI agents "
            "support healthcare."
        ),
        credibility="medium",
    )

    retriever = MultiSourceRetriever(
        tavily_retriever=(
            FakeRetriever(
                [tavily_source]
            )
        ),
        arxiv_retriever=(
            FakeRetriever(
                [arxiv_source]
            )
        ),
    )

    collection = retriever.search(
        "AI agents healthcare",
        web_results=3,
        paper_results=2,
    )

    assert (
        len(collection.sources)
        == 2
    )

    providers = {
        source.provider
        for source
        in collection.sources
    }

    assert providers == {
        "tavily",
        "arxiv",
    }


def test_multi_source_retriever_removes_duplicate_urls():
    first = ResearchSource(
        id="web-arxiv",
        title=(
            "AI Agents in Healthcare"
        ),
        url=(
            "https://arxiv.org/"
            "abs/2601.00001v1"
        ),
        domain="arxiv.org",
        source_type="web",
        provider="tavily",
        snippet=(
            "AI agents healthcare."
        ),
        relevance_score=0.8,
    )

    duplicate = ResearchSource(
        id="paper-arxiv",
        title=(
            "AI Agents in Healthcare"
        ),
        url=(
            "http://arxiv.org/"
            "abs/2601.00001v2"
        ),
        domain="arxiv.org",
        source_type="paper",
        provider="arxiv",
        snippet=(
            "AI agents healthcare."
        ),
        credibility="medium",
    )

    retriever = MultiSourceRetriever(
        tavily_retriever=(
            FakeRetriever(
                [first]
            )
        ),
        arxiv_retriever=(
            FakeRetriever(
                [duplicate]
            )
        ),
    )

    collection = retriever.search(
        "AI agents healthcare"
    )

    assert (
        collection.total_found
        == 1
    )

    assert (
        len(collection.sources)
        == 1
    )


def test_more_relevant_sources_rank_higher():
    irrelevant = ResearchSource(
        id="paper-old",
        title=(
            "Quantum Decision Making "
            "by Social Agents"
        ),
        url=(
            "https://arxiv.org/"
            "abs/1202.4918"
        ),
        domain="arxiv.org",
        source_type="paper",
        provider="arxiv",
        snippet=(
            "Decision theory and "
            "social agents."
        ),
    )

    relevant = ResearchSource(
        id="paper-healthcare",
        title=(
            "Autonomous AI Agents "
            "in Healthcare"
        ),
        url=(
            "https://arxiv.org/"
            "abs/2603.17419"
        ),
        domain="arxiv.org",
        source_type="paper",
        provider="arxiv",
        snippet=(
            "Healthcare AI agents "
            "for clinical systems."
        ),
    )

    retriever = MultiSourceRetriever(
        tavily_retriever=(
            FakeRetriever([])
        ),
        arxiv_retriever=(
            FakeRetriever(
                [
                    irrelevant,
                    relevant,
                ]
            )
        ),
    )

    collection = retriever.search(
        "AI agents healthcare"
    )

    assert (
        collection.sources[0].id
        == "paper-healthcare"
    )

    assert (
        collection.sources[0]
        .relevance_score
        >
        collection.sources[1]
        .relevance_score
    )


def test_multi_source_retriever_limits_results():
    sources = [
        ResearchSource(
            id=f"web-{index}",
            title=(
                f"AI Healthcare "
                f"Source {index}"
            ),
            url=(
                "https://example.com/"
                f"{index}"
            ),
            domain="example.com",
            provider="tavily",
            snippet=(
                "AI healthcare agents"
            ),
            relevance_score=(
                0.9 - index * 0.05
            ),
        )
        for index in range(5)
    ]

    retriever = MultiSourceRetriever(
        tavily_retriever=(
            FakeRetriever(
                sources
            )
        ),
        arxiv_retriever=(
            FakeRetriever([])
        ),
    )

    collection = retriever.search(
        "AI healthcare agents",
        max_sources=3,
    )

    assert (
        len(collection.sources)
        == 3
    )


def test_empty_question_skips_retrievers():
    tavily = FakeRetriever([])

    arxiv = FakeRetriever([])

    retriever = MultiSourceRetriever(
        tavily_retriever=tavily,
        arxiv_retriever=arxiv,
    )

    collection = retriever.search(
        "   "
    )

    assert collection.sources == []

    assert (
        collection.total_found
        == 0
    )

    assert tavily.last_question is None

    assert arxiv.last_question is None