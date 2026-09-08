import logging
import os
import time
from enum import StrEnum

from google import genai
from google.genai import types

from backend.config import load_backend_env


load_backend_env()

logger = logging.getLogger(__name__)
DEFAULT_MODEL = "gemini-3.6-flash"
DEFAULT_TIMEOUT_MS = 120_000
DEFAULT_MAX_ATTEMPTS = 2


class GeminiErrorCategory(StrEnum):
    TRANSIENT_UNAVAILABLE = "transient_unavailable"
    TEMPORARY_RATE_LIMIT = "temporary_rate_limit"
    QUOTA_EXHAUSTED = "quota_exhausted"
    MODEL_QUOTA_EXHAUSTED = "model_quota_exhausted"
    AUTHENTICATION = "authentication"
    INVALID_REQUEST = "invalid_request"
    UNKNOWN = "unknown"


class GeminiProviderError(Exception):
    def __init__(
        self,
        message: str,
        *,
        code: int | None,
        category: GeminiErrorCategory,
        model: str,
        attempts: int,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.category = category
        self.model = model
        self.attempts = attempts


_client: genai.Client | None = None
_client_config: tuple[str, int] | None = None


def _env_int(name: str, default: int, minimum: int) -> int:
    try:
        return max(int(os.getenv(name, str(default))), minimum)
    except ValueError:
        return default


def _configured_model(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _request_timeout_ms() -> int:
    return _env_int("GEMINI_REQUEST_TIMEOUT_MS", DEFAULT_TIMEOUT_MS, 1_000)


def _max_attempts() -> int:
    return min(_env_int("GEMINI_MAX_ATTEMPTS", DEFAULT_MAX_ATTEMPTS, 1), 3)


def get_gemini_configuration() -> dict[str, int | str | bool]:
    load_backend_env()
    return {
        "primary_model": _configured_model("GEMINI_PRIMARY_MODEL", DEFAULT_MODEL),
        "fallback_model": _configured_model("GEMINI_FALLBACK_MODEL"),
        "timeout_ms": _request_timeout_ms(),
        "max_attempts": _max_attempts(),
        "google_api_key_configured": bool(os.getenv("GOOGLE_API_KEY")),
        "gemini_api_key_configured": bool(os.getenv("GEMINI_API_KEY")),
    }


def _quota_metadata(error: BaseException) -> list[str]:
    values: list[str] = []
    response_json = getattr(error, "response_json", None)
    if response_json is None:
        response_json = getattr(error, "details", None)

    def collect(value: object, key: str = "") -> None:
        if isinstance(value, dict):
            for child_key, child_value in value.items():
                if child_key in {
                    "quotaId",
                    "quotaMetric",
                    "quotaDimensions",
                }:
                    collect(child_value, child_key)
                else:
                    collect(child_value)
        elif isinstance(value, (list, tuple)):
            for item in value:
                collect(item, key)
        elif key in {"quotaId", "quotaMetric", "quotaDimensions"}:
            values.append(str(value))

    collect(response_json)
    return values


def classify_gemini_error(error: BaseException) -> GeminiErrorCategory:
    code = getattr(error, "code", None)
    message = str(error).lower()

    if code in {401, 403} or any(
        marker in message
        for marker in ("api key", "authentication", "permission denied")
    ):
        return GeminiErrorCategory.AUTHENTICATION

    if code == 429:
        quota_metadata = _quota_metadata(error)
        if any("permodel" in value.lower() for value in quota_metadata):
            return GeminiErrorCategory.MODEL_QUOTA_EXHAUSTED
        if any(
            marker in message
            for marker in (
                "quota",
                "resource_exhausted",
                "resource exhausted",
                "daily limit",
                "per-minute limit",
            )
        ):
            return GeminiErrorCategory.QUOTA_EXHAUSTED
        return GeminiErrorCategory.TEMPORARY_RATE_LIMIT

    if code in {408, 500, 502, 503, 504} or any(
        marker in message
        for marker in ("timeout", "timed out", "unavailable", "overloaded")
    ):
        return GeminiErrorCategory.TRANSIENT_UNAVAILABLE

    if code in {400, 404} or any(
        marker in message
        for marker in ("invalid argument", "invalid request", "not found")
    ):
        return GeminiErrorCategory.INVALID_REQUEST

    return GeminiErrorCategory.UNKNOWN


def _provider_code(error: BaseException) -> int | None:
    code = getattr(error, "code", None)
    return code if isinstance(code, int) else None


def _get_api_key() -> str:
    api_key = (
        os.getenv("GOOGLE_API_KEY")
        or os.getenv("GEMINI_API_KEY")
    )
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY or GEMINI_API_KEY is not configured."
        )
    return api_key


def get_gemini_client() -> genai.Client:
    global _client, _client_config

    api_key = _get_api_key()

    config = (api_key, _request_timeout_ms())
    if _client is None or _client_config != config:
        _client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=config[1],
                retry_options=types.HttpRetryOptions(attempts=1),
            ),
        )
        _client_config = config

    return _client


def _generate_once(client: genai.Client, prompt: str, model: str, agent: str) -> str:
    started_at = time.perf_counter()
    try:
        response = client.models.generate_content(model=model, contents=prompt)
    except Exception as error:
        elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)
        category = classify_gemini_error(error)
        logger.warning(
            "[Gemini] agent=%s model=%s status=%s category=%s duration_ms=%.2f",
            agent,
            model,
            _provider_code(error) or "unknown",
            category.value,
            elapsed_ms,
        )
        raise

    elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)
    logger.info(
        "[Gemini] agent=%s model=%s status=success duration_ms=%.2f",
        agent,
        model,
        elapsed_ms,
    )
    return response.text or ""


def _generate_with_retries(client: genai.Client, prompt: str, model: str, agent: str) -> str:
    last_error: BaseException | None = None
    max_attempts = _max_attempts()

    for attempt in range(1, max_attempts + 1):
        try:
            return _generate_once(client, prompt, model, agent)
        except Exception as error:
            last_error = error
            category = classify_gemini_error(error)
            logger.info(
                "[Gemini] agent=%s model=%s attempt=%d/%d category=%s",
                agent,
                model,
                attempt,
                max_attempts,
                category.value,
            )
            if category not in {
                GeminiErrorCategory.TRANSIENT_UNAVAILABLE,
                GeminiErrorCategory.TEMPORARY_RATE_LIMIT,
            } or attempt >= max_attempts:
                break
            time.sleep(min(0.25 * (2 ** (attempt - 1)), 1.0))

    assert last_error is not None
    raise GeminiProviderError(
        str(last_error),
        code=_provider_code(last_error),
        category=classify_gemini_error(last_error),
        model=model,
        attempts=attempt,
    ) from last_error


def generate_response(
    prompt: str,
    *,
    model: str | None = None,
    agent: str = "unknown",
) -> str:
    client = get_gemini_client()
    selected_model = model or _configured_model("GEMINI_PRIMARY_MODEL", DEFAULT_MODEL)

    try:
        return _generate_with_retries(client, prompt, selected_model, agent)
    except GeminiProviderError as primary_error:
        fallback_model = _configured_model("GEMINI_FALLBACK_MODEL")
        eligible = primary_error.category in {
            GeminiErrorCategory.TRANSIENT_UNAVAILABLE,
            GeminiErrorCategory.TEMPORARY_RATE_LIMIT,
            GeminiErrorCategory.MODEL_QUOTA_EXHAUSTED,
        }
        if not fallback_model or fallback_model == selected_model or not eligible:
            raise

        if primary_error.category == GeminiErrorCategory.MODEL_QUOTA_EXHAUSTED:
            logger.warning(
                "[Gemini] agent=%s activating configured fallback model=%s "
                "after model-specific quota exhaustion",
                agent,
                fallback_model,
            )
            return _generate_with_retries(
                client,
                prompt,
                fallback_model,
                agent,
            )

        logger.warning(
            "[Gemini] agent=%s activating configured fallback model=%s category=%s",
            agent,
            fallback_model,
            primary_error.category.value,
        )
        return _generate_with_retries(client, prompt, fallback_model, agent)