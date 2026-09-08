from backend.models.source import (
    ResearchSource,
)
from backend.retrieval.citations import (
    build_citation_registry,
)


DEFAULT_MAX_CHARS_PER_SOURCE = 1800


def _clean_text(
    value: str,
) -> str:
    return " ".join(
        value.split()
    )


def _truncate_text(
    value: str,
    max_chars: int,
) -> str:
    clean_value = _clean_text(
        value
    )

    if len(clean_value) <= max_chars:
        return clean_value

    truncated = clean_value[
        :max_chars
    ].rstrip()

    return f"{truncated}..."


def _format_authors(
    authors: list[str],
) -> str:
    if not authors:
        return "Not provided"

    return ", ".join(
        authors
    )


def _format_validation_notes(
    notes: list[str],
) -> str:
    if not notes:
        return "None"

    return " ".join(
        notes
    )


def prepare_evidence(
    sources: list[ResearchSource],
    max_chars_per_source: int = (
        DEFAULT_MAX_CHARS_PER_SOURCE
    ),
) -> tuple[
    str,
    list[ResearchSource],
]:
    """
    Convert validated sources into a
    compact evidence context for the LLM.

    Citation IDs are assigned according
    to source order:

    S1, S2, S3, ...

    The returned source copies contain
    the same citation IDs used inside
    the evidence context.
    """

    if not sources:
        return "", []

    registry = build_citation_registry(sources)
    prepared_sources = registry.sources

    evidence_blocks: list[str] = []


    for prepared_source in prepared_sources:
        citation_id = prepared_source.citation_id
        assert citation_id is not None


        evidence_text = (
            prepared_source.content
            or prepared_source.snippet
        )

        evidence_text = _truncate_text(
            evidence_text,
            max_chars_per_source,
        )


        block_lines = [
            f"[{citation_id}]",
            (
                "Title: "
                f"{prepared_source.title}"
            ),
            (
                "Provider: "
                f"{prepared_source.provider}"
            ),
            (
                "Source type: "
                f"{prepared_source.source_type}"
            ),
            (
                "Domain: "
                f"{prepared_source.domain}"
            ),
            (
                "Credibility: "
                f"{prepared_source.credibility}"
            ),
            (
                "Relevance score: "
                f"{prepared_source.relevance_score:.3f}"
            ),
            (
                "Authors: "
                f"{_format_authors(prepared_source.authors)}"
            ),
            (
                "Published: "
                f"{prepared_source.published_date or 'Not provided'}"
            ),
            (
                "URL: "
                f"{prepared_source.url}"
            ),
            (
                "Validation notes: "
                f"{_format_validation_notes(
                    prepared_source.validation_notes
                )}"
            ),
            (
                "Evidence: "
                f"{evidence_text or 'No evidence text provided.'}"
            ),
        ]

        evidence_blocks.append(
            "\n".join(
                block_lines
            )
        )


    evidence_context = (
        "\n\n".join(
            evidence_blocks
        )
    )

    return (
        evidence_context,
        prepared_sources,
    )