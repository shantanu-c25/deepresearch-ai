from collections.abc import Callable, Sequence
import os
from pathlib import Path
from threading import Lock
from typing import Any

import numpy as np


class SentenceTransformerEmbeddingProvider:
    """Lazy ONNX embeddings using sentence-transformers/all-MiniLM-L6-v2."""

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        model: Any | None = None,
        model_factory: Callable[[str], Any] | None = None,
        normalize_embeddings: bool = True,
        batch_size: int = 4,
        model_path: str | Path | None = None,
        tokenizer: Any | None = None,
    ) -> None:
        if batch_size < 1:
            raise ValueError("batch_size must be positive")
        self.model_name = model_name
        self._model = model
        self._model_factory = model_factory
        self.normalize_embeddings = normalize_embeddings
        self.batch_size = batch_size
        self.model_path = Path(model_path) if model_path is not None else None
        self._tokenizer = tokenizer
        self._model_lock = Lock()

    def _get_model(self) -> Any:
        if self._model is None:
            with self._model_lock:
                if self._model is None:
                    if self._model_factory is not None:
                        self._model = self._model_factory(self.model_name)
                    else:
                        try:
                            import onnxruntime as ort
                            from tokenizers import Tokenizer
                        except ImportError as exc:
                            raise RuntimeError(
                                "onnxruntime and tokenizers are required for local embeddings"
                            ) from exc
                        model_directory = self._resolve_model_directory()
                        tokenizer_path = model_directory / "tokenizer.json"
                        model_file = model_directory / "model.onnx"
                        if not tokenizer_path.exists() or not model_file.exists():
                            raise RuntimeError(
                                "the ONNX embedding model is not available; "
                                "run the backend ONNX model export during the build"
                            )
                        self._tokenizer = self._tokenizer or Tokenizer.from_file(
                            str(tokenizer_path)
                        )
                        self._tokenizer.enable_truncation(max_length=256)
                        self._tokenizer.enable_padding(
                            pad_id=0,
                            pad_token="[PAD]",
                        )
                        session_options = ort.SessionOptions()
                        session_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
                        session_options.intra_op_num_threads = 1
                        session_options.inter_op_num_threads = 1
                        session_options.enable_mem_pattern = False
                        self._model = ort.InferenceSession(
                            str(model_file),
                            sess_options=session_options,
                            providers=["CPUExecutionProvider"],
                        )
        return self._model

    def _resolve_model_directory(self) -> Path:
        if self.model_path is not None:
            return self.model_path
        configured_path = os.getenv("RAG_ONNX_MODEL_PATH")
        if configured_path:
            return Path(configured_path)
        return Path(__file__).resolve().parent / "onnx_model"

    def _encode_onnx(self, values: list[str], model: Any) -> list[list[float]]:
        if self._tokenizer is None:
            raise RuntimeError("the ONNX tokenizer is not initialized")
        output_names = [output.name for output in model.get_outputs()]
        vectors: list[list[float]] = []
        for start in range(0, len(values), self.batch_size):
            encoded = self._tokenizer.encode_batch(values[start : start + self.batch_size])
            inputs = {
                "input_ids": np.asarray(
                    [item.ids for item in encoded],
                    dtype=np.int64,
                ),
                "attention_mask": np.asarray(
                    [item.attention_mask for item in encoded],
                    dtype=np.int64,
                ),
            }
            outputs = dict(zip(output_names, model.run(None, inputs)))
            token_embeddings = np.asarray(
                outputs["token_embeddings"]
                if "token_embeddings" in outputs
                else outputs["last_hidden_state"]
            )
            attention_mask = inputs["attention_mask"].astype(np.float32)[..., None]
            pooled = (token_embeddings * attention_mask).sum(axis=1) / np.maximum(
                attention_mask.sum(axis=1),
                1e-9,
            )
            if self.normalize_embeddings:
                pooled /= np.maximum(
                    np.linalg.norm(pooled, axis=1, keepdims=True),
                    1e-12,
                )
            vectors.extend(pooled.tolist())
        return vectors

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        values = list(texts)
        if not values:
            return []
        if any(not text.strip() for text in values):
            raise ValueError("texts cannot contain blank values")

        model = self._get_model()
        if hasattr(model, "encode"):
            vectors = model.encode(
                values,
                batch_size=self.batch_size,
                normalize_embeddings=self.normalize_embeddings,
            )
            return [[float(value) for value in vector] for vector in vectors]
        return self._encode_onnx(values, model)

    def embed_query(self, query: str) -> list[float]:
        if not query.strip():
            raise ValueError("query cannot be blank")
        return self.embed_texts([query])[0]