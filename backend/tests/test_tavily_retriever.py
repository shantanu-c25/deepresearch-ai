from backend.retrieval.tavily_retriever import (
    TavilyRetriever,
)


class FakeTavilyClient:
    def __init__(self):
        self.last_request = None


    def search(self, **kwargs):
        self.last_request = kwargs

        return {
            "results": [
                {
                    "title": (
                        "Artificial "
                        "Intelligence "
                        "in Healthcare"
                    ),
                    "url": (
                        "https://www."
                        "who.int/"
                        "example-ai"
                    ),
                    "content": (
                        "AI can support "
                        "healthcare "
                        "decision making."
                    ),
                    "score": 0.87,
                }
            ]
        }


def test_tavily_retriever_normalizes_results():
    client = FakeTavilyClient()

    retriever = TavilyRetriever(
        client=client
    )

    sources = retriever.search(
        (
            "What are the benefits "
            "of AI agents in "
            "healthcare?"
        ),
        max_results=3,
    )

    assert len(sources) == 1

    source = sources[0]

    assert source.provider == (
        "tavily"
    )

    assert source.source_type == (
        "web"
    )

    assert source.domain == (
        "who.int"
    )

    assert source.relevance_score == (
        0.87
    )

    assert source.title == (
        "Artificial Intelligence "
        "in Healthcare"
    )

    assert (
        source.snippet
        == source.content
    )


def test_tavily_retriever_uses_basic_search():
    client = FakeTavilyClient()

    retriever = TavilyRetriever(
        client=client
    )

    retriever.search(
        "AI healthcare",
        max_results=4,
    )

    assert (
        client.last_request[
            "search_depth"
        ]
        == "basic"
    )

    assert (
        client.last_request[
            "max_results"
        ]
        == 4
    )

    assert (
        client.last_request[
            "include_answer"
        ]
        is False
    )


def test_empty_question_returns_no_sources():
    client = FakeTavilyClient()

    retriever = TavilyRetriever(
        client=client
    )

    sources = retriever.search(
        "   "
    )

    assert sources == []

    assert (
        client.last_request
        is None
    )