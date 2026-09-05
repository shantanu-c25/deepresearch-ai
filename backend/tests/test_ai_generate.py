from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_generate_ai_response(monkeypatch):
    def fake_generate_response(prompt: str) -> str:
        return "Mock AI response"

    monkeypatch.setattr(
        "backend.main.generate_response",
        fake_generate_response,
    )

    response = client.post(
        "/ai/generate",
        json={
            "prompt": "Explain AI simply.",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "response": "Mock AI response",
    }