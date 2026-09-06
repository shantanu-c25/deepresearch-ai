import hashlib
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from dotenv import load_dotenv
from tavily import TavilyClient

from backend.models.source import ResearchSource


BACKEND_ENV_PATH = (
    Path(__file__).resolve().parents[1]
    / ".env"
)

load_dotenv()
load_dotenv(
    BACKEND_ENV_PATH,
    override=False,
)


def _build_source_id(
    url: str,
) -> str:
    digest = hashlib.sha256(
        url.encode("utf-8")
    ).hexdigest()[:12]

    return f"tavily-{digest}"


def _extract_domain(
    url: str,
) -> str:
    parsed = urlparse(url)

    domain = (
        parsed.netloc
        .lower()
        .removeprefix("www.")
    )

    return domain


def _normalize_score(
    value: Any,
) -> float:
    try:
        score = float(value)
    except (
        TypeError,
        ValueError,
    ):
        return 0.0

    return max(
        0.0,
        min(score, 1.0),
    )


class TavilyRetriever:
    def __init__(
        self,
        api_key: str | None = None,
        client: Any | None = None,
    ) -> None:
        if client is not None:
            self.client = client

            return

        resolved_api_key = (
            api_key
            or os.getenv(
                "TAVILY_API_KEY"
            )
        )

        if not resolved_api_key:
            raise RuntimeError(
                "TAVILY_API_KEY is "
                "not configured."
            )

        self.client = TavilyClient(
            api_key=resolved_api_key
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

        response = self.client.search(
            query=clean_question,
            search_depth="basic",
            max_results=max_results,
            include_answer=False,
            include_raw_content=False,
        )

        raw_results = response.get(
            "results",
            [],
        )

        sources: list[
            ResearchSource
        ] = []


        for item in raw_results:
            title = str(
                item.get(
                    "title",
                    "",
                )
            ).strip()

            url = str(
                item.get(
                    "url",
                    "",
                )
            ).strip()

            if not title or not url:
                continue

            content = str(
                item.get(
                    "content",
                    "",
                )
            ).strip()

            source = ResearchSource(
                id=_build_source_id(
                    url
                ),
                title=title,
                url=url,
                domain=_extract_domain(
                    url
                ),
                source_type="web",
                provider="tavily",
                snippet=content,
                content=content,
                relevance_score=(
                    _normalize_score(
                        item.get(
                            "score"
                        )
                    )
                ),
                credibility="unrated",
            )

            sources.append(source)


        return sources