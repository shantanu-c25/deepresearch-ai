from urllib.parse import urlparse

from backend.models.source import (
    ResearchSource,
    SourceCollection,
    ValidatedSourceCollection,
)


_HIGH_CREDIBILITY_DOMAINS = {
    "who.int",
    "nih.gov",
    "ncbi.nlm.nih.gov",
    "cdc.gov",
    "fda.gov",
    "nature.com",
    "science.org",
}


_KNOWN_VENDOR_DOMAINS = {
    "ibm.com",
    "oracle.com",
    "microsoft.com",
    "google.com",
    "cloud.google.com",
    "aws.amazon.com",
}


def _is_government_domain(
    domain: str,
) -> bool:
    domain = domain.lower()

    return (
        domain.endswith(".gov")
        or ".gov." in domain
        or domain.endswith(".gov.in")
    )


def _is_academic_domain(
    domain: str,
) -> bool:
    domain = domain.lower()

    return (
        domain.endswith(".edu")
        or ".edu." in domain
        or domain.endswith(".ac.uk")
        or domain.endswith(".ac.in")
        or domain.endswith(".edu.au")
    )


def _classify_credibility(
    source: ResearchSource,
) -> tuple[str, list[str]]:
    domain = (
        source.domain
        .lower()
        .removeprefix("www.")
    )

    notes: list[str] = []


    if source.provider == "arxiv":
        notes.append(
            "arXiv is a preprint repository; "
            "peer review is not guaranteed."
        )

        return (
            "medium",
            notes,
        )


    if (
        domain
        in _HIGH_CREDIBILITY_DOMAINS
        or _is_government_domain(
            domain
        )
        or _is_academic_domain(
            domain
        )
    ):
        notes.append(
            "Institutional, government, "
            "academic, or established "
            "research source."
        )

        return (
            "high",
            notes,
        )


    if domain in _KNOWN_VENDOR_DOMAINS:
        notes.append(
            "Vendor-authored source; "
            "useful for industry perspective "
            "but may contain commercial bias."
        )

        return (
            "medium",
            notes,
        )


    notes.append(
        "Source credibility has not been "
        "independently established."
    )

    return (
        "low",
        notes,
    )


def _uses_https(
    url: str,
) -> bool:
    parsed = urlparse(url)

    return (
        parsed.scheme.lower()
        == "https"
    )


class SourceValidator:
    def __init__(
        self,
        min_relevance: float = 0.20,
    ) -> None:
        self.min_relevance = (
            min_relevance
        )


    def validate_source(
        self,
        source: ResearchSource,
    ) -> ResearchSource:
        validated = source.model_copy(
            deep=True
        )

        credibility, notes = (
            _classify_credibility(
                validated
            )
        )

        validated.credibility = (
            credibility
        )

        validated.validation_notes = [
            *notes
        ]


        if (
            validated.relevance_score
            < self.min_relevance
        ):
            validated.validation_status = (
                "rejected"
            )

            validated.validation_notes.append(
                "Rejected because relevance "
                "score is below the minimum "
                "threshold."
            )

            return validated


        if not _uses_https(
            validated.url
        ):
            validated.validation_notes.append(
                "Source does not use HTTPS."
            )


        if credibility == "low":
            validated.validation_status = (
                "needs-review"
            )

            return validated


        validated.validation_status = (
            "accepted"
        )

        return validated


    def validate_collection(
        self,
        collection: SourceCollection,
    ) -> ValidatedSourceCollection:
        accepted_sources: list[
            ResearchSource
        ] = []

        review_sources: list[
            ResearchSource
        ] = []

        rejected_sources: list[
            ResearchSource
        ] = []


        for source in collection.sources:
            validated = (
                self.validate_source(
                    source
                )
            )

            if (
                validated.validation_status
                == "rejected"
            ):
                rejected_sources.append(
                    validated
                )

                continue


            if (
                validated.validation_status
                == "needs-review"
            ):
                review_sources.append(
                    validated
                )

                continue


            accepted_sources.append(
                validated
            )


        return ValidatedSourceCollection(
            question=collection.question,
            accepted_sources=(
                accepted_sources
            ),
            review_sources=(
                review_sources
            ),
            rejected_sources=(
                rejected_sources
            ),
            total_evaluated=len(
                collection.sources
            ),
        )