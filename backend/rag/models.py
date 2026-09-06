from typing import Any

from pydantic import BaseModel, Field, field_validator


class DocumentChunk(BaseModel):
    id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    citation_id: str | None = None
    source_title: str
    source_url: str
    content: str = Field(min_length=1)
    chunk_index: int = Field(ge=0)
    char_start: int = Field(ge=0)
    char_end: int = Field(ge=1)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("content")
    @classmethod
    def reject_blank_content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("chunk content cannot be blank")
        return value

    @field_validator("char_end")
    @classmethod
    def validate_range(cls, value: int, info) -> int:
        start = info.data.get("char_start")
        if start is not None and value <= start:
            raise ValueError("char_end must be greater than char_start")
        return value


class RetrievedChunk(DocumentChunk):
    relevance_score: float = Field(ge=0.0, le=1.0)
    rank: int = Field(ge=1)


class RAGContext(BaseModel):
    question: str = Field(min_length=1)
    retrieved_chunks: list[RetrievedChunk] = Field(default_factory=list)
    context_text: str = ""
    total_retrieved: int = Field(ge=0)
    total_sources: int = Field(default=0, ge=0)
    total_chunks: int = Field(default=0, ge=0)

    @field_validator("question")
    @classmethod
    def reject_blank_question(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("question cannot be blank")
        return value