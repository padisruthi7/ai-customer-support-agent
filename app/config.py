import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _resolve_database_url() -> str:
    configured = os.getenv("DATABASE_URL")
    if configured:
        return configured

    if os.getenv("VERCEL") or os.getenv("VERCEL_ENV"):
        tmp_dir = Path("/tmp")
        tmp_dir.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{tmp_dir / 'customer_support.db'}"

    return f"sqlite:///{BASE_DIR / 'customer_support.db'}"


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DATABASE_URL = _resolve_database_url()
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.0-flash")
