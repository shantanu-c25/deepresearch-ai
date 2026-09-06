import hashlib
from typing import Any

import arxiv

from backend.models.source import (
    ResearchSource,
)
from backend.retrieval.query_builder import (
    build_arxiv_query,
)


def _build_source_id(
    url: str,
) -> str:
    digest = hashlib.sha256(
        url.encode("utf-8")
    ).hexdigest()[:12]

    return f"arxiv-{digest}"


def _clean_text(
    value: str,
) -> str:
    return " ".join(
        value.split()
    )


class ArxivRetriever:
    def __init__(
        self,
        client: Any | None = None,
    ) -> None:
        self.client = (
            client
            if client is not None
            else arxiv.Client()
        )


    def search(
        self,
        question: str,
        max_results: int = 5,
    ) -> list[ResearchSource]:
        clean_question = (
            question.strip()
        )

        if not clean_question:
            return []

        arxiv_query = (
            build_arxiv_query(
                clean_question
            )
        )

        search = arxiv.Search(
            query=arxiv_query,
            max_results=max_results,
            sort_by=(
                arxiv
                .SortCriterion
                .Relevance
            ),
        )

        sources: list[
            ResearchSource
        ] = []


        for result in self.client.results(
            search
        ):
            title = _clean_text(
                str(result.title)
            )

            url = str(
                result.entry_id
            ).strip()

            summary = _clean_text(
                str(result.summary)
            )

            if not title or not url:
                continue

            authors = [
                author.name
                for author
                in result.authors
            ]

            published_date = None

            if result.published:
                published_date = (
                    result
                    .published
                    .date()
                    .isoformat()
                )

            source = ResearchSource(
                id=_build_source_id(
                    url
                ),
                title=title,
                url=url,
                domain="arxiv.org",
                source_type="paper",
                provider="arxiv",
                snippet=summary,
                content=summary,
                authors=authors,
                published_date=(
                    published_date
                ),
                credibility="medium",
            )

            sources.append(
                source
            )


        return sources