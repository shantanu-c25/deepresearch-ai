import math
from collections.abc import Sequence

from backend.rag.models import DocumentChunk, RetrievedChunk


def _cosine_similarity(
    first: Sequence[float],
    second: Sequence[float],
) -> float:
    numerator = sum(left * right for left, right in zip(first, second))
    first_norm = math.sqrt(sum(value * value for value in first))
    second_norm = math.sqrt(sum(value * value for value in second))
    if not first_norm or not second_norm:
        return 0.0
    return numerator / (first_norm * second_norm)


class InMemoryVectorStore:
    """A deterministic local store; relevance is cosine similarity clamped to 0..1."""

    def __init__(self) -> None:
        self._items: list[tuple[DocumentChunk, list[float]]] = []
        self._dimension: int | None = None

    def add(
        self,
        chunks: Sequence[DocumentChunk],
        embeddings: Sequence[Sequence[float]],
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings must have matching lengths")
        for chunk, embedding in zip(chunks, embeddings):
            vector = [float(value) for value in embedding]
            if not vector:
                raise ValueError("embeddings cannot be empty")
            if self._dimension is None:
                self._dimension = len(vector)
            if len(vector) != self._dimension:
                raise ValueError("all embeddings must have the same dimension")
            self._items.append((chunk, vector))

    def similarity_search(
        self,
        query_embedding: Sequence[float],
        limit: int,
    ) -> list[RetrievedChunk]:
        if limit < 1:
            raise ValueError("limit must be positive")
        query = [float(value) for value in query_embedding]
        if self._dimension is not None and len(query) != self._dimension:
            raise ValueError("query embedding has an inconsistent dimension")
        ranked = [
            (
                max(0.0, min(1.0, _cosine_similarity(query, embedding))),
                chunk,
            )
            for chunk, embedding in self._items
        ]
        ranked.sort(key=lambda item: (-item[0], item[1].id))
        return [
            RetrievedChunk(
                **chunk.model_dump(),
                relevance_score=round(score, 6),
                rank=index,
            )
            for index, (score, chunk) in enumerate(ranked[:limit], start=1)
        ]