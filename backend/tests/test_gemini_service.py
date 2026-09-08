import logging
import os

import pytest
from google.genai.errors import ClientError

from backend.config import ENV_PATH, load_backend_env
import backend.services.gemini_service as gemini_service


class FakeProviderError(Exception):
    def __init__(self, code: int, message: str, response_json=None):
        super().__init__(message)
        self.code = code
        self.response_json = response_json


class FakeModels:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def generate_content(self, *, model, contents):
        self.calls.append((model, contents))
        response = next(self.responses)
        if isinstance(response, BaseException):
            raise response
        return response


class FakeClient:
    def __init__(self, responses):
        self.models = FakeModels(responses)


@pytest.fixture(autouse=True)
def reset_client(monkeypatch):
    monkeypatch.setattr(gemini_service, "_client", None)
    monkeypatch.setattr(gemini_service, "_client_config", None)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.delenv("GEMINI_FALLBACK_MODEL", raising=False)
    monkeypatch.setenv("GEMINI_MAX_ATTEMPTS", "2")
    monkeypatch.setattr(gemini_service.time, "sleep", lambda seconds: None)


def response(text):
    return type("Response", (), {"text": text})()


def model_quota_client_error():
    return ClientError(
        429,
        {
            "error": {
                "code": 429,
                "message": "... quota exceeded ... model: gemini-3.6-flash ...",
                "status": "RESOURCE_EXHAUSTED",
                "details": [
                    {"@type": "type.googleapis.com/google.rpc.Help"},
                    {
                        "@type": "type.googleapis.com/google.rpc.QuotaFailure",
                        "violations": [
                            {
                                "quotaMetric": "generativelanguage.googleapis.com/generate_content_free_tier_requests",
                                "quotaId": "GenerateRequestsPerDayPerModel-FreeTier",
                                "quotaDimensions": {
                                    "location": "global",
                                    "model": "gemini-3.6-flash",
                                },
                                "quotaValue": "20",
                            }
                        ],
                    },
                    {
                        "@type": "type.googleapis.com/google.rpc.RetryInfo",
                        "retryDelay": "21s",
                    },
                ],
            }
        },
    )


def test_google_api_key_only(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "google-key")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    assert gemini_service._get_api_key() == "google-key"


def test_gemini_api_key_only(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-key")

    assert gemini_service._get_api_key() == "gemini-key"


def test_backend_env_path_is_independent_of_current_working_directory(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GEMINI_PRIMARY_MODEL", raising=False)

    assert load_backend_env() == ENV_PATH
    assert os.environ["GEMINI_PRIMARY_MODEL"] == "gemini-3.6-flash"


def test_configured_models_timeout_and_attempts_are_resolved(monkeypatch):
    for name in (
        "GEMINI_PRIMARY_MODEL",
        "GEMINI_FALLBACK_MODEL",
        "GEMINI_REQUEST_TIMEOUT_MS",
        "GEMINI_MAX_ATTEMPTS",
    ):
        monkeypatch.delenv(name, raising=False)

    configuration = gemini_service.get_gemini_configuration()

    assert configuration["primary_model"] == "gemini-3.6-flash"
    assert configuration["fallback_model"] == "gemini-3.5-flash-lite"
    assert configuration["timeout_ms"] == 120000
    assert configuration["max_attempts"] == 2


def test_configuration_is_loaded_before_values_are_resolved(monkeypatch):
    monkeypatch.setenv("GEMINI_PRIMARY_MODEL", "post-import-model")
    assert gemini_service._configured_model("GEMINI_PRIMARY_MODEL") == "post-import-model"


def test_diagnostic_configuration_does_not_expose_key_values(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "google-secret")
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-secret")

    configuration = gemini_service.get_gemini_configuration()

    assert configuration["google_api_key_configured"] is True
    assert configuration["gemini_api_key_configured"] is True
    assert "google-secret" not in str(configuration)
    assert "gemini-secret" not in str(configuration)


def test_google_api_key_takes_precedence(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "google-key")
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-key")

    assert gemini_service._get_api_key() == "google-key"


def test_missing_api_keys_fail_clearly(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="GOOGLE_API_KEY or GEMINI_API_KEY"):
        gemini_service._get_api_key()


def test_error_categories():
    assert gemini_service.classify_gemini_error(
        FakeProviderError(503, "UNAVAILABLE")
    ) == gemini_service.GeminiErrorCategory.TRANSIENT_UNAVAILABLE
    assert gemini_service.classify_gemini_error(
        FakeProviderError(429, "Too Many Requests")
    ) == gemini_service.GeminiErrorCategory.TEMPORARY_RATE_LIMIT
    assert gemini_service.classify_gemini_error(
        FakeProviderError(429, "RESOURCE_EXHAUSTED quota")
    ) == gemini_service.GeminiErrorCategory.QUOTA_EXHAUSTED
    assert gemini_service.classify_gemini_error(
        FakeProviderError(
            429,
            "RESOURCE_EXHAUSTED",
            {
                "quotaId": "GenerateRequestsPerDayPerProjectPerModel-FreeTier",
                "quotaMetric": "generativelanguage.googleapis.com/generate_content_free_tier_requests",
            },
        )
    ) == gemini_service.GeminiErrorCategory.MODEL_QUOTA_EXHAUSTED
    assert gemini_service.classify_gemini_error(
        FakeProviderError(401, "invalid API key")
    ) == gemini_service.GeminiErrorCategory.AUTHENTICATION
    assert gemini_service.classify_gemini_error(
        FakeProviderError(400, "invalid argument")
    ) == gemini_service.GeminiErrorCategory.INVALID_REQUEST


def test_real_client_error_model_quota_classifies_from_details():
    assert gemini_service.classify_gemini_error(
        model_quota_client_error()
    ) == gemini_service.GeminiErrorCategory.MODEL_QUOTA_EXHAUSTED


def test_success_has_one_model_call(monkeypatch):
    client = FakeClient([response("ok")])
    monkeypatch.setattr(gemini_service, "get_gemini_client", lambda: client)

    assert gemini_service.generate_response("prompt", agent="research") == "ok"
    assert len(client.models.calls) == 1


def test_transient_failure_retries_once_then_succeeds(monkeypatch):
    client = FakeClient([
        FakeProviderError(503, "UNAVAILABLE"),
        response("recovered"),
    ])
    monkeypatch.setattr(gemini_service, "get_gemini_client", lambda: client)

    assert gemini_service.generate_response("prompt") == "recovered"
    assert len(client.models.calls) == 2


def test_retry_limit_stops_and_hard_quota_does_not_retry(monkeypatch):
    transient_client = FakeClient([
        FakeProviderError(503, "UNAVAILABLE"),
        FakeProviderError(503, "UNAVAILABLE"),
    ])
    monkeypatch.setattr(gemini_service, "get_gemini_client", lambda: transient_client)

    with pytest.raises(gemini_service.GeminiProviderError) as transient_error:
        gemini_service.generate_response("prompt")
    assert transient_error.value.category == gemini_service.GeminiErrorCategory.TRANSIENT_UNAVAILABLE
    assert len(transient_client.models.calls) == 2

    quota_client = FakeClient([
        FakeProviderError(429, "RESOURCE_EXHAUSTED quota")
    ])
    monkeypatch.setattr(gemini_service, "get_gemini_client", lambda: quota_client)

    with pytest.raises(gemini_service.GeminiProviderError) as quota_error:
        gemini_service.generate_response("prompt")
    assert quota_error.value.category == gemini_service.GeminiErrorCategory.QUOTA_EXHAUSTED
    assert len(quota_client.models.calls) == 1


def test_fallback_model_only_handles_eligible_failure(monkeypatch):
    client = FakeClient([
        FakeProviderError(503, "UNAVAILABLE"),
        FakeProviderError(503, "UNAVAILABLE"),
        response("fallback success"),
    ])
    monkeypatch.setattr(gemini_service, "get_gemini_client", lambda: client)
    monkeypatch.setenv("GEMINI_FALLBACK_MODEL", "configured-fallback")

    assert gemini_service.generate_response("prompt") == "fallback success"
    assert [model for model, _ in client.models.calls] == [
        "gemini-3.6-flash",
        "gemini-3.6-flash",
        "configured-fallback",
    ]


def test_model_quota_uses_fallback_immediately_without_retry(monkeypatch):
    model_quota = FakeProviderError(
        429,
        "RESOURCE_EXHAUSTED",
        {
            "quotaId": "GenerateRequestsPerDayPerProjectPerModel-FreeTier",
        },
    )
    client = FakeClient([model_quota, response("fallback success")])
    monkeypatch.setattr(gemini_service, "get_gemini_client", lambda: client)
    monkeypatch.setenv("GEMINI_FALLBACK_MODEL", "configured-fallback")

    assert gemini_service.generate_response("prompt") == "fallback success"
    assert [model for model, _ in client.models.calls] == [
        "gemini-3.6-flash",
        "configured-fallback",
    ]


def test_real_client_error_uses_configured_fallback_without_sleep(monkeypatch):
    client = FakeClient([model_quota_client_error(), response("fallback success")])
    sleep_calls = []
    monkeypatch.setattr(gemini_service, "get_gemini_client", lambda: client)
    monkeypatch.setenv("GEMINI_FALLBACK_MODEL", "gemini-3.5-flash-lite")
    monkeypatch.setattr(gemini_service.time, "sleep", sleep_calls.append)

    assert gemini_service.generate_response("prompt") == "fallback success"
    assert [model for model, _ in client.models.calls] == [
        "gemini-3.6-flash",
        "gemini-3.5-flash-lite",
    ]
    assert sleep_calls == []


def test_real_client_error_fallback_quota_propagates(monkeypatch):
    client = FakeClient([model_quota_client_error(), model_quota_client_error()])
    monkeypatch.setattr(gemini_service, "get_gemini_client", lambda: client)
    monkeypatch.setenv("GEMINI_FALLBACK_MODEL", "gemini-3.5-flash-lite")

    with pytest.raises(gemini_service.GeminiProviderError) as error:
        gemini_service.generate_response("prompt")

    assert error.value.code == 429
    assert error.value.category == gemini_service.GeminiErrorCategory.MODEL_QUOTA_EXHAUSTED
    assert [model for model, _ in client.models.calls] == [
        "gemini-3.6-flash",
        "gemini-3.5-flash-lite",
    ]


def test_model_quota_fallback_quota_returns_hard_quota_error(monkeypatch):
    model_quota = {
        "quotaId": "GenerateRequestsPerDayPerProjectPerModel-FreeTier",
    }
    client = FakeClient([
        FakeProviderError(429, "RESOURCE_EXHAUSTED", model_quota),
        FakeProviderError(429, "RESOURCE_EXHAUSTED", model_quota),
    ])
    monkeypatch.setattr(gemini_service, "get_gemini_client", lambda: client)
    monkeypatch.setenv("GEMINI_FALLBACK_MODEL", "configured-fallback")

    with pytest.raises(gemini_service.GeminiProviderError) as error:
        gemini_service.generate_response("prompt")

    assert error.value.category == gemini_service.GeminiErrorCategory.MODEL_QUOTA_EXHAUSTED
    assert [model for model, _ in client.models.calls] == [
        "gemini-3.6-flash",
        "configured-fallback",
    ]


def test_project_quota_does_not_use_fallback(monkeypatch):
    client = FakeClient([
        FakeProviderError(
            429,
            "RESOURCE_EXHAUSTED quota",
            {"quotaId": "GenerateRequestsPerDayPerProject-FreeTier"},
        )
    ])
    monkeypatch.setattr(gemini_service, "get_gemini_client", lambda: client)
    monkeypatch.setenv("GEMINI_FALLBACK_MODEL", "configured-fallback")

    with pytest.raises(gemini_service.GeminiProviderError) as error:
        gemini_service.generate_response("prompt")

    assert error.value.category == gemini_service.GeminiErrorCategory.QUOTA_EXHAUSTED
    assert [model for model, _ in client.models.calls] == ["gemini-3.6-flash"]


def test_unknown_hard_quota_does_not_use_fallback(monkeypatch):
    client = FakeClient([
        FakeProviderError(429, "RESOURCE_EXHAUSTED quota")
    ])
    monkeypatch.setattr(gemini_service, "get_gemini_client", lambda: client)
    monkeypatch.setenv("GEMINI_FALLBACK_MODEL", "configured-fallback")

    with pytest.raises(gemini_service.GeminiProviderError) as error:
        gemini_service.generate_response("prompt")

    assert error.value.category == gemini_service.GeminiErrorCategory.QUOTA_EXHAUSTED
    assert [model for model, _ in client.models.calls] == ["gemini-3.6-flash"]


def test_authentication_error_does_not_use_fallback(monkeypatch):
    client = FakeClient([FakeProviderError(401, "invalid API key")])
    monkeypatch.setattr(gemini_service, "get_gemini_client", lambda: client)
    monkeypatch.setenv("GEMINI_FALLBACK_MODEL", "configured-fallback")

    with pytest.raises(gemini_service.GeminiProviderError) as error:
        gemini_service.generate_response("prompt")
    assert error.value.category == gemini_service.GeminiErrorCategory.AUTHENTICATION
    assert len(client.models.calls) == 1


def test_logs_do_not_include_prompt_or_api_key(monkeypatch, caplog):
    client = FakeClient([response("ok")])
    monkeypatch.setattr(gemini_service, "get_gemini_client", lambda: client)
    secret_prompt = "private uploaded document content"

    with caplog.at_level(logging.INFO):
        gemini_service.generate_response(secret_prompt, agent="research")

    logs = caplog.text
    assert secret_prompt not in logs
    assert "test-key" not in logs


def test_client_uses_configured_timeout_and_disables_sdk_retry(monkeypatch):
    captured = {}

    class FakeGenaiClient:
        def __init__(self, *, api_key, http_options):
            captured["api_key"] = api_key
            captured["http_options"] = http_options

    monkeypatch.setattr(gemini_service.genai, "Client", FakeGenaiClient)
    monkeypatch.setenv("GEMINI_REQUEST_TIMEOUT_MS", "45000")

    gemini_service.get_gemini_client()

    assert captured["api_key"] == "test-key"
    assert captured["http_options"].timeout == 45000
    assert captured["http_options"].retry_options.attempts == 1
