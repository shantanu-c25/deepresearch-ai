import os

from backend.config import get_allowed_origins, load_backend_env


def test_allowed_origins_trims_and_ignores_empty_values(monkeypatch):
    monkeypatch.setenv(
        "ALLOWED_ORIGINS",
        " https://research.example , ,http://localhost:3000 ",
    )

    assert get_allowed_origins() == [
        "https://research.example",
        "http://localhost:3000",
    ]


def test_allowed_origins_default_to_local_frontends(monkeypatch):
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)

    assert get_allowed_origins() == [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


def test_host_environment_values_are_not_overwritten_by_local_dotenv(monkeypatch):
    monkeypatch.setenv("GEMINI_PRIMARY_MODEL", "platform-model")

    load_backend_env()

    assert os.getenv("GEMINI_PRIMARY_MODEL") == "platform-model"