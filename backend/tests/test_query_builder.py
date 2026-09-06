from backend.retrieval.query_builder import (
    build_arxiv_query,
)


def test_build_arxiv_query_removes_question_words():
    query = build_arxiv_query(
        (
            "What are the main benefits "
            "and risks of AI agents "
            "in healthcare?"
        )
    )

    assert "all:what" not in query
    assert "all:the" not in query
    assert "all:main" not in query

    assert "all:ai" in query
    assert "all:agents" in query
    assert "all:healthcare" in query


def test_build_arxiv_query_removes_analysis_intent():
    query = build_arxiv_query(
        (
            "What are the main benefits "
            "and risks of AI agents "
            "in healthcare?"
        )
    )

    assert "all:benefits" not in query
    assert "all:risks" not in query

    assert query == (
        "all:ai AND "
        "all:agents AND "
        "all:healthcare"
    )


def test_build_arxiv_query_uses_and():
    query = build_arxiv_query(
        "AI agents healthcare"
    )

    assert query == (
        "all:ai AND "
        "all:agents AND "
        "all:healthcare"
    )


def test_build_arxiv_query_removes_duplicates():
    query = build_arxiv_query(
        (
            "AI AI agents agents "
            "healthcare healthcare"
        )
    )

    assert query.count(
        "all:ai"
    ) == 1

    assert query.count(
        "all:agents"
    ) == 1

    assert query.count(
        "all:healthcare"
    ) == 1


def test_build_arxiv_query_limits_terms():
    query = build_arxiv_query(
        (
            "artificial intelligence "
            "agents healthcare clinical "
            "diagnosis treatment safety "
            "privacy security ethics "
            "automation"
        )
    )

    assert (
        len(
            query.split(
                " AND "
            )
        )
        == 6
    )


def test_empty_query_returns_empty_string():
    query = build_arxiv_query(
        "   "
    )

    assert query == ""