import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai


ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)


def get_gemini_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")

    return genai.Client(api_key=api_key)


def generate_response(prompt: str) -> str:
    client = get_gemini_client()

    started_at = time.perf_counter()

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )

    elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)
    print(f"[Gemini] generate_content completed in {elapsed_ms}ms")

    return response.text or ""