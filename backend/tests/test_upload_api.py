import threading

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


def test_health_remains_responsive_during_upload_indexing(monkeypatch):
    indexing_started = threading.Event()
    release_indexing = threading.Event()
    original_index_uploaded_document = main._index_uploaded_document

    class FakeService:
        def add_uploaded_document(self, uploaded):
            return []

    shared_service = FakeService()
    monkeypatch.setattr(main, "rag_pipeline_service", shared_service)

    def blocked_indexing(data, filename, content_type):
        indexing_started.set()
        assert release_indexing.wait(timeout=2)
        return original_index_uploaded_document(data, filename, content_type)

    monkeypatch.setattr(main, "_index_uploaded_document", blocked_indexing)
    client = TestClient(main.app)
    upload_result = {}

    upload_thread = threading.Thread(
        target=lambda: upload_result.update(
            response=client.post(
                "/rag/documents",
                files={"file": ("evidence.txt", b"evidence", "text/plain")},
            )
        )
    )
    upload_thread.start()

    assert indexing_started.wait(timeout=2)

    health_result = {}
    health_thread = threading.Thread(
        target=lambda: health_result.update(response=client.get("/health"))
    )
    health_thread.start()
    health_thread.join(timeout=2)

    release_indexing.set()
    upload_thread.join(timeout=2)
    health_thread.join(timeout=2)

    assert not health_thread.is_alive()
    assert health_result["response"].status_code == 200
    assert upload_result["response"].status_code == 201
    assert main.rag_pipeline_service is shared_service