import pytest

from backend.models.source import ResearchSource, SourceCollection
from backend.rag.service import RAGPipelineService


class FakeSourceRetriever:
    def search(self, question, max_sources=8):
        return SourceCollection(
            question=question,
            sources=[
                ResearchSource(
                    id="source-1",
                    title="Healthcare agents",
                    url="https://example.com/healthcare",
                    domain="example.com",
                    provider="arxiv",
                    content="AI agents can support healthcare workflows.",
                    relevance_score=0.9,
                )
            ],
            total_found=1,
        )


class FakeEmbeddingProvider:
    def embed_texts(self, texts):
        return [[1.0, 0.0] for _ in texts]

    def embed_query(self, query):
        return [1.0, 0.0]


def test_rag_service_composes_sources_into_grounded_context():
    context = RAGPipelineService(
        source_retriever=FakeSourceRetriever(),
        embedding_provider=FakeEmbeddingProvider(),
    ).retrieve("healthcare agents", top_k=3)

    assert context.total_sources == 1
    assert context.total_chunks == 1
    assert context.total_retrieved == 1
    assert context.retrieved_chunks[0].citation_id == "S1"
    assert "[S1]" in context.context_text


def test_rag_service_rejects_blank_questions():
    with pytest.raises(ValueError):
        RAGPipelineService(
            source_retriever=FakeSourceRetriever(),
            embedding_provider=FakeEmbeddingProvider(),
        ).retrieve(" ")


def test_rag_service_does_not_fail_for_empty_accepted_corpus():
    class EmptyRetriever:
        def search(self, question, max_sources=8):
            return SourceCollection(question=question, sources=[])

    context = RAGPipelineService(
        source_retriever=EmptyRetriever(),
        embedding_provider=FakeEmbeddingProvider(),
    ).retrieve("question")

    assert context.total_sources == 0
    assert context.total_chunks == 0
    assert context.retrieved_chunks == []