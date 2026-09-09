import threading

from fastapi.testclient import TestClient

from backend.main import app
import backend.main as main

client = TestClient(app)


def test_research_endpoint(monkeypatch):
    def fake_run_deep_research(question: str):
        return {
            "question": question,
            "research_brief": "mock research brief",
            "critical_analysis": "mock critical analysis",
            "insights": "mock insights",
            "final_report": "mock final report",
        }

    monkeypatch.setattr(
        "backend.main.run_deep_research",
        fake_run_deep_research,
    )

    response = client.post(
        "/research",
        json={
            "question": "What is agentic AI?",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "question": "What is agentic AI?",
        "research_brief": "mock research brief",
        "critical_analysis": "mock critical analysis",
        "insights": "mock insights",
        "final_report": "mock final report",
        "sources": [],
    }


def test_health_remains_responsive_during_research(monkeypatch):
    research_started = threading.Event()
    release_research = threading.Event()

    def blocked_research(question: str):
        research_started.set()
        assert release_research.wait(timeout=2)
        return {
            "question": question,
            "research_brief": "mock research brief",
            "critical_analysis": "mock critical analysis",
            "insights": "mock insights",
            "final_report": "mock final report",
        }

    monkeypatch.setattr(main, "run_deep_research", blocked_research)
    research_result = {}

    research_thread = threading.Thread(
        target=lambda: research_result.update(
            response=client.post(
                "/research",
                json={"question": "What is agentic AI?"},
            )
        )
    )
    research_thread.start()

    assert research_started.wait(timeout=2)

    health_result = {}
    health_thread = threading.Thread(
        target=lambda: health_result.update(response=client.get("/health"))
    )
    health_thread.start()
    health_thread.join(timeout=2)

    release_research.set()
    research_thread.join(timeout=2)
    health_thread.join(timeout=2)

    assert not health_thread.is_alive()
    assert health_result["response"].status_code == 200
    assert research_result["response"].status_code == 200


def test_research_endpoint_returns_429_when_gemini_quota_is_exhausted(
    monkeypatch,
):
    class FakeQuotaError(Exception):
        code = 429

    def fake_run_deep_research(question: str):
        raise FakeQuotaError("RESOURCE_EXHAUSTED")

    monkeypatch.setattr(
        "backend.main.run_deep_research",
        fake_run_deep_research,
    )

    response = client.post(
        "/research",
        json={
            "question": "What are the benefits of AI agents?",
        },
    )

    assert response.status_code == 429
    assert response.json() == {
        "detail": (
            "Gemini free-tier quota has been reached. "
            "Please try again later."
        )
    }


def test_research_endpoint_returns_503_when_gemini_is_unavailable(
    monkeypatch,
):
    from backend.services.gemini_service import (
        GeminiErrorCategory,
        GeminiProviderError,
    )

    def fake_run_deep_research(question: str):
        raise GeminiProviderError(
            "provider unavailable",
            code=503,
            category=GeminiErrorCategory.TRANSIENT_UNAVAILABLE,
            model="gemini-3.6-flash",
            attempts=2,
        )

    monkeypatch.setattr(
        "backend.main.run_deep_research",
        fake_run_deep_research,
    )

    response = client.post(
        "/research",
        json={"question": "What is unavailable?"},
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": (
            "The Gemini provider is temporarily unavailable. "
            "Please try again shortly."
        )
    }
def test_research_endpoint_returns_sources(
    monkeypatch,
):
    def fake_run_deep_research(
        question: str,
    ):
        return {
            "question": question,
            "research_brief": (
                "Research brief"
            ),
            "critical_analysis": (
                "Critical analysis"
            ),
            "insights": "Insights",
            "final_report": (
                "Final report"
            ),
            "sources": [
                {
                    "id": "source-1",
                    "citation_id": "S1",
                    "title": (
                        "AI Agents "
                        "in Healthcare"
                    ),
                    "url": (
                        "https://www."
                        "ibm.com/example"
                    ),
                    "domain": "ibm.com",
                    "provider": "tavily",
                    "source_type": "web",
                    "snippet": (
                        "Evidence text"
                    ),
                    "content": (
                        "Evidence text"
                    ),
                    "authors": [],
                    "published_date": None,
                    "relevance_score": 0.82,
                    "credibility": "medium",
                    "validation_status": (
                        "accepted"
                    ),
                    "validation_notes": [
                        (
                            "Vendor-authored "
                            "source."
                        )
                    ],
                }
            ],
        }

    monkeypatch.setattr(
        main,
        "run_deep_research",
        fake_run_deep_research,
    )

    response = client.post(
        "/research",
        json={
            "question": (
                "AI agents healthcare"
            )
        },
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    assert (
        len(data["sources"])
        == 1
    )

    source = data["sources"][0]

    assert (
        source["citation_id"]
        == "S1"
    )

    assert (
        source["provider"]
        == "tavily"
    )

    assert (
        source["title"]
        == (
            "AI Agents "
            "in Healthcare"
        )
    )

    assert (
        source["credibility"]
        == "medium"
    )