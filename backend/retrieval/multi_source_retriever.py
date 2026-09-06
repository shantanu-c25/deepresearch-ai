import re
from collections.abc import Iterable
from urllib.parse import urlparse

from backend.models.source import (
    ResearchSource,
    SourceCollection,
)
from backend.retrieval.arxiv_retriever import (
    ArxivRetriever,
)
from backend.retrieval.tavily_retriever import (
    TavilyRetriever,
)


_STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "into",
    "is",
    "it",
    "main",
    "of",
    "on",
    "or",
    "the",
    "to",
    "using",
    "what",
    "with",
}


def _tokenize(
    text: str,
) -> set[str]:
    words = re.findall(
        r"[a-z0-9]+",
        text.lower(),
    )

    return {
        word
        for word in words
        if (
            len(word) > 2
            and word not in _STOP_WORDS
        )
    }


def _canonical_url(
    url: str,
) -> str:
    parsed = urlparse(
        url.strip()
    )

    domain = (
        parsed.netloc
        .lower()
        .removeprefix("www.")
    )

    path = (
        parsed.path
        .rstrip("/")
    )

    if domain == "arxiv.org":
        path = re.sub(
            r"v\d+$",
            "",
            path,
        )

    return (
        f"{domain}{path}"
        .lower()
    )


def _normalize_title(
    title: str,
) -> str:
    normalized = re.sub(
        r"[^a-z0-9]+",
        " ",
        title.lower(),
    )

    return " ".join(
        normalized.split()
    )


def _lexical_relevance(
    question: str,
    source: ResearchSource,
) -> float:
    question_tokens = _tokenize(
        question
    )

    if not question_tokens:
        return 0.0

    title_tokens = _tokenize(
        source.title
    )

    body_tokens = _tokenize(
        " ".join(
            [
                source.snippet,
                source.content,
            ]
        )
    )

    title_overlap = (
        len(
            question_tokens
            & title_tokens
        )
        / len(question_tokens)
    )

    body_overlap = (
        len(
            question_tokens
            & body_tokens
        )
        / len(question_tokens)
    )

    score = (
        title_overlap * 0.7
        + body_overlap * 0.3
    )

    return round(
        min(score, 1.0),
        4,
    )


def _rerank_score(
    question: str,
    source: ResearchSource,
) -> float:
    lexical_score = (
        _lexical_relevance(
            question,
            source,
        )
    )

    provider_score = (
        source.relevance_score
    )

    if (
        source.provider == "tavily"
        and provider_score > 0
    ):
        combined_score = (
            provider_score * 0.65
            + lexical_score * 0.35
        )
    else:
        combined_score = (
            lexical_score
        )

    return round(
        min(
            max(
                combined_score,
                0.0,
            ),
            1.0,
        ),
        4,
    )


def _prefer_source(
    current: ResearchSource,
    candidate: ResearchSource,
) -> ResearchSource:
    if (
        candidate.relevance_score
        > current.relevance_score
    ):
        return candidate

    if (
        candidate.relevance_score
        < current.relevance_score
    ):
        return current

    if (
        candidate.source_type == "paper"
        and current.source_type != "paper"
    ):
        return candidate

    return current


def _same_source(
    first: ResearchSource,
    second: ResearchSource,
) -> bool:
    first_url = _canonical_url(
        first.url
    )

    second_url = _canonical_url(
        second.url
    )

    if first_url == second_url:
        return True

    first_title = _normalize_title(
        first.title
    )

    second_title = _normalize_title(
        second.title
    )

    same_title = (
        bool(first_title)
        and first_title
        == second_title
    )

    same_domain = (
        first.domain.lower()
        == second.domain.lower()
    )

    return (
        same_title
        and same_domain
    )


def _deduplicate_sources(
    sources: Iterable[
        ResearchSource
    ],
) -> list[ResearchSource]:
    unique_sources: list[
        ResearchSource
    ] = []

    for source in sources:
        duplicate_index = None

        for index, existing in enumerate(
            unique_sources
        ):
            if _same_source(
                existing,
                source,
            ):
                duplicate_index = index
                break

        if duplicate_index is None:
            unique_sources.append(
                source
            )

            continue

        existing = unique_sources[
            duplicate_index
        ]

        unique_sources[
            duplicate_index
        ] = _prefer_source(
            existing,
            source,
        )

    return unique_sources


class MultiSourceRetriever:
    def __init__(
        self,
        tavily_retriever=None,
        arxiv_retriever=None,
    ) -> None:
        self.tavily_retriever = (
            tavily_retriever
            if tavily_retriever
            is not None
            else TavilyRetriever()
        )

        self.arxiv_retriever = (
            arxiv_retriever
            if arxiv_retriever
            is not None
            else ArxivRetriever()
        )


    def search(
        self,
        question: str,
        web_results: int = 5,
        paper_results: int = 5,
        max_sources: int = 8,
    ) -> SourceCollection:
        clean_question = (
            question.strip()
        )

        if not clean_question:
            return SourceCollection(
                question=question,
                sources=[],
                total_found=0,
            )

        web_sources = (
            self.tavily_retriever
            .search(
                clean_question,
                max_results=web_results,
            )
        )

        paper_sources = (
            self.arxiv_retriever
            .search(
                clean_question,
                max_results=paper_results,
            )
        )

        combined = [
            *web_sources,
            *paper_sources,
        ]

        reranked: list[
            ResearchSource
        ] = []

        for source in combined:
            source_copy = (
                source.model_copy(
                    deep=True
                )
            )

            source_copy.relevance_score = (
                _rerank_score(
                    clean_question,
                    source_copy,
                )
            )

            reranked.append(
                source_copy
            )

        unique_sources = (
            _deduplicate_sources(
                reranked
            )
        )

        ranked_sources = sorted(
            unique_sources,
            key=lambda source: (
                source.relevance_score
            ),
            reverse=True,
        )

        selected_sources = (
            ranked_sources[
                :max_sources
            ]
        )

        return SourceCollection(
            question=clean_question,
            sources=selected_sources,
            total_found=len(
                unique_sources
            ),
        )