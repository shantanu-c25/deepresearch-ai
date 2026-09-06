from typing import Protocol

from backend.models.source import ResearchSource


class SourceRetriever(Protocol):
    def search(
        self,
        question: str,
        max_results: int = 5,
    ) -> list[ResearchSource]:
        """
        Retrieve sources relevant to a
        research question.

        Every retrieval provider must
        return normalized ResearchSource
        objects.
        """
        ...