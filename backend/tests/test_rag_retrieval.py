import threading
from math import isclose

import pytest

from backend.rag.embeddings import SentenceTransformerEmbeddingProvider
from backend.rag.loader import SourceDocument
from backend.rag.models import DocumentChunk
from backend.rag.semantic import SemanticRAGRetriever
from backend.rag.vector_store import InMemoryVectorStore


def make_chunk(chunk_id: str, citation: str, content: str) -> DocumentChunk:
    return DocumentChunk(
        id=chunk_id,
        source_id=chunk_id,
        citation_id=citation,
        source_title=f"Title {citation}",
        source_url=f"https://example.com/{chunk_id}",
        content=content,
        chunk_index=0,
        char_start=0,
        char_end=len(content),
    )


class FakeEmbeddingProvider:
    def __init__(self, vectors):
        self.vectors = vectors

    def embed_texts(self, texts):
        return [self.vectors[text] for text in texts]

    def embed_query(self, query):
        return self.vectors[query]


def test_vector_store_ranks_cosine_similarity_and_preserves_provenance():
    chunks = [
        make_chunk("a", "S1", "first"),
        make_chunk("b", "S2", "second"),
        make_chunk("c", "S3", "third"),
    ]
    store = InMemoryVectorStore()
    store.add(chunks, [[1, 0, 0], [0, 1, 0], [0.7, 0.7, 0]])

    results = store.similarity_search([0, 1, 0], limit=2)

    assert [result.citation_id for result in results] == ["S2", "S3"]
    assert results[0].rank == 1
    assert results[0].relevance_score == 1.0
    assert results[1].source_url == "https://example.com/c"


def test_vector_store_resolves_ties_by_chunk_id_and_validates_inputs():
    chunks = [make_chunk("b", "S2", "b"), make_chunk("a", "S1", "a")]
    store = InMemoryVectorStore()
    store.add(chunks, [[1, 0], [1, 0]])

    assert [result.id for result in store.similarity_search([1, 0], 2)] == ["a", "b"]
    with pytest.raises(ValueError):
        store.add(chunks, [[1, 0]])
    with pytest.raises(ValueError):
        store.similarity_search([1, 0], 0)


def test_semantic_retriever_formats_context_and_top_k():
    chunks = [
        make_chunk("a", "S1", "alpha evidence"),
        make_chunk("b", "S2", "beta evidence"),
    ]
    vectors = {
        "alpha evidence": [1, 0],
        "beta evidence": [0, 1],
        "find beta": [0, 1],
    }
    context = SemanticRAGRetriever(
        chunks,
        FakeEmbeddingProvider(vectors),
        InMemoryVectorStore(),
    ).retrieve("find beta", top_k=1)

    assert context.total_retrieved == 1
    assert context.retrieved_chunks[0].citation_id == "S2"
    assert "[S2]" in context.context_text
    assert "https://example.com/b" in context.context_text
    assert "[S1]" not in context.context_text


def test_semantic_retriever_handles_empty_corpus_without_embedding_query():
    class FailingQueryProvider(FakeEmbeddingProvider):
        def embed_query(self, query):
            raise AssertionError("empty corpus should not embed a query")

    context = SemanticRAGRetriever(
        [],
        FailingQueryProvider({}),
        InMemoryVectorStore(),
    ).retrieve("question")

    assert context.total_retrieved == 0
    assert context.context_text == ""


def test_embedding_provider_is_lazy_and_accepts_injected_model():
    class FakeModel:
        def encode(self, texts, batch_size, normalize_embeddings):
            assert batch_size == 4
            assert normalize_embeddings is True
            return [[float(len(texts)), 1.0] for _ in texts]

    provider = SentenceTransformerEmbeddingProvider(model=FakeModel())

    assert provider.embed_texts([]) == []
    assert provider.embed_query("query") == [1.0, 1.0]
    with pytest.raises(ValueError):
        provider.embed_query(" ")


def test_embedding_provider_initializes_model_once():
    factory_calls = []

    class FakeModel:
        def encode(self, texts, batch_size, normalize_embeddings):
            return [[1.0, 0.0] for _ in texts]

    def model_factory(model_name):
        factory_calls.append(model_name)
        return FakeModel()

    provider = SentenceTransformerEmbeddingProvider(model_factory=model_factory)

    provider.embed_texts(["first"])
    provider.embed_texts(["second"])

    assert factory_calls == ["sentence-transformers/all-MiniLM-L6-v2"]


def test_embedding_provider_does_not_duplicate_concurrent_model_initialization():
    factory_calls = []
    factory_started = threading.Event()
    release_factory = threading.Event()

    class FakeModel:
        def encode(self, texts, batch_size, normalize_embeddings):
            return [[1.0, 0.0] for _ in texts]

    def model_factory(model_name):
        factory_calls.append(model_name)
        factory_started.set()
        assert release_factory.wait(timeout=2)
        return FakeModel()

    provider = SentenceTransformerEmbeddingProvider(model_factory=model_factory)
    threads = [
        threading.Thread(target=provider.embed_texts, args=(["text"],))
        for _ in range(2)
    ]
    for thread in threads:
        thread.start()

    assert factory_started.wait(timeout=2)
    release_factory.set()
    for thread in threads:
        thread.join(timeout=2)

    assert all(not thread.is_alive() for thread in threads)
    assert factory_calls == ["sentence-transformers/all-MiniLM-L6-v2"]


def test_onnx_embedding_batches_and_normalizes_vectors():
    class FakeEncoding:
        def __init__(self, ids, attention_mask):
            self.ids = ids
            self.attention_mask = attention_mask

    class FakeTokenizer:
        def encode_batch(self, values):
            return [
                FakeEncoding([1, 2, 0], [1, 1, 0])
                for _ in values
            ]

    class FakeOutput:
        name = "token_embeddings"

    class FakeSession:
        def __init__(self):
            self.calls = []

        def get_outputs(self):
            return [FakeOutput()]

        def run(self, output_names, inputs):
            self.calls.append(inputs)
            batch_size = len(inputs["input_ids"])
            return [
                [
                    [[3.0, 4.0] for _ in range(3)]
                    for _ in range(batch_size)
                ]
            ]

    session = FakeSession()
    provider = SentenceTransformerEmbeddingProvider(
        model=session,
        tokenizer=FakeTokenizer(),
        batch_size=1,
    )

    vectors = provider.embed_texts(["first", "second"])

    assert len(vectors) == 2
    assert all(len(vector) == 2 for vector in vectors)
    assert all(isclose(vector[0], 0.6) for vector in vectors)
    assert all(isclose(vector[1], 0.8) for vector in vectors)
    assert len(session.calls) == 2