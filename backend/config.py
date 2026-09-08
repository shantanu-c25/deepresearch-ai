from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parent
ENV_PATH = BACKEND_DIR / ".env"


def load_backend_env() -> Path:
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    return ENV_PATH
