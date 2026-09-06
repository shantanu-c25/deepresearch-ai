from fastapi.testclient import TestClient

import backend.main as main
from backend.rag.models import RAGContext


client = TestClient(main.app)


class FakeRAGService:
    def __init__(self):
        self.calls = []

    def retrieve(self, question, top_k):
        self.calls.append((question, top_k))
        return RAGContext(
            question=question,
            retrieved_chunks=[],
            context_text="",
            total_retrieved=0,
            total_sources=2,
            total_chunks=4,
        )


def test_rag_endpoint_returns_schema_and_preserves_top_k(monkeypatch):
    service = FakeRAGService()
    monkeypatch.setattr(main, "rag_pipeline_service", service)

    response = client.post(
        "/rag/retrieve",
        json={"question": "AI in healthcare", "top_k": 7},
    )

    assert response.status_code == 200
    assert response.json()["question"] == "AI in healthcare"
    assert response.json()["total_sources"] == 2
    assert response.json()["total_chunks"] == 4
    assert service.calls == [("AI in healthcare", 7)]


def test_rag_endpoint_rejects_blank_question_and_invalid_top_k():
    blank = client.post("/rag/retrieve", json={"question": "  "})
    invalid_top_k = client.post(
        "/rag/retrieve",
        json={"question": "question", "top_k": 21},
    )

    assert blank.status_code == 422
    assert invalid_top_k.status_code == 422


def test_rag_endpoint_maps_rag_failures_without_calling_gemini(monkeypatch):
    class BrokenService:
        def retrieve(self, question, top_k):
            raise RuntimeError("embedding failed")

    def unexpected_gemini_call(question):
        raise AssertionError("Gemini must not be used by RAG retrieval")

    monkeypatch.setattr(main, "rag_pipeline_service", BrokenService())
    monkeypatch.setattr(main, "run_deep_research", unexpected_gemini_call)

    response = client.post(
        "/rag/retrieve",
        json={"question": "question", "top_k": 1},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "RAG retrieval failed."