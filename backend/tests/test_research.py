from fastapi.testclient import TestClient

from backend.main import app


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
    }