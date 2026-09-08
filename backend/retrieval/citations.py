import re
from collections.abc import Iterable

from pydantic import BaseModel, Field

from backend.models.source import ResearchSource


_CITATION_PATTERN = re.compile(r"\[S(?P<number>[1-9][0-9]*)\]")


class CitationRegistryEntry(BaseModel):
    citation_id: str
    original_citation_id: str | None = None
    source: ResearchSource


class CitationRegistry(BaseModel):
    entries: list[CitationRegistryEntry] = Field(default_factory=list)

    @property
    def sources(self) -> list[ResearchSource]:
        return [entry.source for entry in self.entries]

    @property
    def allowed_ids(self) -> set[str]:
        return {entry.citation_id for entry in self.entries}

    @property
    def source_to_citation(self) -> dict[str, str]:
        return {
            entry.source.id: entry.citation_id
            for entry in self.entries
        }


class CitationValidation(BaseModel):
    cited_ids: list[str] = Field(default_factory=list)
    valid_ids: list[str] = Field(default_factory=list)
    invalid_ids: list[str] = Field(default_factory=list)
    uncited_ids: list[str] = Field(default_factory=list)


def _is_valid_citation_id(value: str | None) -> bool:
    return bool(
        value
        and re.fullmatch(r"S[1-9][0-9]*", value)
    )


def _source_key(source: ResearchSource) -> str:
    return source.id


def build_citation_registry(
    sources: Iterable[ResearchSource],
) -> CitationRegistry:
    """Build one deterministic, source-level citation inventory."""
    unique_sources: list[ResearchSource] = []
    seen_source_ids: set[str] = set()

    for source in sources:
        source_key = _source_key(source)
        if source_key in seen_source_ids:
            continue
        seen_source_ids.add(source_key)
        unique_sources.append(source)

    preserved_ids: dict[str, str] = {}
    used_ids: set[str] = set()
    for source in unique_sources:
        citation_id = source.citation_id
        if (
            _is_valid_citation_id(citation_id)
            and citation_id not in used_ids
        ):
            preserved_ids[source.id] = citation_id
            used_ids.add(citation_id)

    next_number = 1
    entries: list[CitationRegistryEntry] = []
    for source in unique_sources:
        citation_id = preserved_ids.get(source.id)
        if citation_id is None:
            while f"S{next_number}" in used_ids:
                next_number += 1
            citation_id = f"S{next_number}"
            used_ids.add(citation_id)
            next_number += 1

        normalized_source = source.model_copy(deep=True)
        normalized_source.citation_id = citation_id
        entries.append(
            CitationRegistryEntry(
                citation_id=citation_id,
                original_citation_id=source.citation_id,
                source=normalized_source,
            )
        )

    return CitationRegistry(entries=entries)


def extract_citation_ids(text: str) -> list[str]:
    """Extract only the supported human-facing citation syntax."""
    return [
        match.group(0)[1:-1]
        for match in _CITATION_PATTERN.finditer(text)
    ]


def normalize_evidence_context(
    context: str,
    registry: CitationRegistry,
) -> str:
    """Replace internal source markers with registry citation markers."""
    normalized = context
    for entry in registry.entries:
        normalized = normalized.replace(
            f"[{entry.source.id}]",
            f"[{entry.citation_id}]",
        )
    return normalized


def validate_citations(
    text: str,
    registry: CitationRegistry,
) -> CitationValidation:
    cited_ids = extract_citation_ids(text)
    unique_cited_ids = list(dict.fromkeys(cited_ids))
    allowed_ids = registry.allowed_ids
    valid_ids = [
        citation_id
        for citation_id in unique_cited_ids
        if citation_id in allowed_ids
    ]
    invalid_ids = [
        citation_id
        for citation_id in unique_cited_ids
        if citation_id not in allowed_ids
    ]
    uncited_ids = [
        citation_id
        for citation_id in registry.entries
        if citation_id.citation_id not in unique_cited_ids
    ]

    return CitationValidation(
        cited_ids=unique_cited_ids,
        valid_ids=valid_ids,
        invalid_ids=invalid_ids,
        uncited_ids=[entry.citation_id for entry in uncited_ids],
    )


def sanitize_invalid_citations(
    text: str,
    registry: CitationRegistry,
) -> tuple[str, CitationValidation]:
    validation = validate_citations(text, registry)
    allowed_ids = registry.allowed_ids

    sanitized = _CITATION_PATTERN.sub(
        lambda match: (
            match.group(0)
            if match.group(0)[1:-1] in allowed_ids
            else ""
        ),
        text,
    )
    sanitized = re.sub(r"[ \t]{2,}", " ", sanitized)
    sanitized = re.sub(r" +([,.!?])", r"\1", sanitized)

    return sanitized, validation
