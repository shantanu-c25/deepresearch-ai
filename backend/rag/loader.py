import re
from dataclasses import dataclass, field

from backend.models.source import ResearchSource


@dataclass(frozen=True)
class SourceDocument:
    source_id: str
    citation_id: str | None
    source_title: str
    source_url: str
    content: str
    metadata: dict[str, object] = field(default_factory=dict)


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


class SourceDocumentLoader:
    def load(self, source: ResearchSource) -> SourceDocument | None:
        raw_content = source.content.strip() or source.snippet.strip()
        content = _clean_text(raw_content)
        if not content:
            return None

        return SourceDocument(
            source_id=source.id,
            citation_id=source.citation_id,
            source_title=source.title,
            source_url=source.url,
            content=content,
            metadata={
                "provider": source.provider,
                "domain": source.domain,
                "source_type": source.source_type,
                "authors": list(source.authors),
                "published_date": source.published_date,
            },
        )

    def load_many(self, sources: list[ResearchSource]) -> list[SourceDocument]:
        return [document for source in sources if (document := self.load(source))]