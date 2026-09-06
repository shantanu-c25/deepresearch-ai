from collections.abc import Callable, Sequence
from typing import Any


class SentenceTransformerEmbeddingProvider:
    """Lazy local embeddings using sentence-transformers/all-MiniLM-L6-v2."""

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        model: Any | None = None,
        model_factory: Callable[[str], Any] | None = None,
        normalize_embeddings: bool = True,
    ) -> None:
        self.model_name = model_name
        self._model = model
        self._model_factory = model_factory
        self.normalize_embeddings = normalize_embeddings

    def _get_model(self) -> Any:
        if self._model is None:
            if self._model_factory is not None:
                self._model = self._model_factory(self.model_name)
            else:
                try:
                    from sentence_transformers import SentenceTransformer
                except ImportError as exc:
                    raise RuntimeError(
                        "sentence-transformers is required for local embeddings"
                    ) from exc
                self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        values = list(texts)
        if not values:
            return []
        if any(not text.strip() for text in values):
            raise ValueError("texts cannot contain blank values")

        vectors = self._get_model().encode(
            values,
            normalize_embeddings=self.normalize_embeddings,
        )
        return [[float(value) for value in vector] for vector in vectors]

    def embed_query(self, query: str) -> list[float]:
        if not query.strip():
            raise ValueError("query cannot be blank")
        return self.embed_texts([query])[0]