from fastapi.testclient import TestClient

import backend.main as main
from backend.rag.service import RAGPipelineService


class EmptySourceRetriever:
    def search(self, question, max_sources=8):
        from backend.models.source import SourceCollection

        return SourceCollection(question=question, sources=[])


class FakeEmbeddingProvider:
    def embed_texts(self, texts):
        return [[1.0, 0.0] for _ in texts]

    def embed_query(self, query):
        return [1.0, 0.0]


def test_upload_indexes_text_and_rag_retrieves_it(monkeypatch):
    service = RAGPipelineService(
        source_retriever=EmptySourceRetriever(),
        embedding_provider=FakeEmbeddingProvider(),
    )
    monkeypatch.setattr(main, "rag_pipeline_service", service)
    client = TestClient(main.app)

    upload = client.post(
        "/rag/documents",
        files={"file": ("evidence.txt", b"Uploaded research evidence", "text/plain")},
    )

    assert upload.status_code == 201
    assert upload.json()["status"] == "indexed"
    assert upload.json()["chunks"] == 1

    retrieval = client.post(
        "/rag/retrieve",
        json={"question": "research evidence", "top_k": 1},
    )

    assert retrieval.status_code == 200
    body = retrieval.json()
    assert body["total_sources"] == 1
    assert body["retrieved_chunks"][0]["metadata"]["source_type"] == "uploaded_document"
    assert "Uploaded research evidence" in body["context_text"]


def test_upload_rejects_unsupported_and_empty_files():
    client = TestClient(main.app)

    unsupported = client.post(
        "/rag/documents",
        files={"file": ("evidence.exe", b"content", "application/octet-stream")},
    )
    empty = client.post(
        "/rag/documents",
        files={"file": ("evidence.txt", b"", "text/plain")},
    )

    assert unsupported.status_code == 415
    assert empty.status_code == 400