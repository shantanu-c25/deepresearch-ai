from typing import Literal

from pydantic import BaseModel, Field


SourceType = Literal[
    "web",
    "news",
    "paper",
    "report",
    "documentation",
    "unknown",
]


SourceProvider = Literal[
    "tavily",
    "arxiv",
    "manual",
]


CredibilityLevel = Literal[
    "high",
    "medium",
    "low",
    "unrated",
]


ValidationStatus = Literal[
    "unreviewed",
    "accepted",
    "needs-review",
    "rejected",
]


class ResearchSource(BaseModel):
    id: str

    citation_id: str | None = None

    title: str

    url: str

    domain: str

    source_type: SourceType = "unknown"

    provider: SourceProvider

    snippet: str = ""

    content: str = ""

    authors: list[str] = Field(
        default_factory=list
    )

    published_date: str | None = None

    relevance_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    credibility: CredibilityLevel = (
        "unrated"
    )

    validation_status: ValidationStatus = (
        "unreviewed"
    )

    validation_notes: list[str] = Field(
        default_factory=list
    )


class SourceCollection(BaseModel):
    question: str

    sources: list[ResearchSource] = Field(
        default_factory=list
    )

    total_found: int = 0


class ValidatedSourceCollection(BaseModel):
    question: str

    accepted_sources: list[
        ResearchSource
    ] = Field(
        default_factory=list
    )

    review_sources: list[
        ResearchSource
    ] = Field(
        default_factory=list
    )

    rejected_sources: list[
        ResearchSource
    ] = Field(
        default_factory=list
    )

    total_evaluated: int = 0