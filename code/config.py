"""Central configuration: paths, env vars, model settings.

Loaded once from .env (if present) and environment variables. Never hardcode
secrets here — ANTHROPIC_API_KEY is read at call time, never stored.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = REPO_ROOT / "dataset"
MEDIA_DIR = DATASET_DIR / "media"
IMAGES_DIR = MEDIA_DIR / "images"
AUDIO_DIR = MEDIA_DIR / "audio"

DATA_DIR = REPO_ROOT / "data"
DB_PATH = DATA_DIR / "processed.db"
CACHE_DIR = DATA_DIR / "cache"
IMAGE_CACHE_DIR = CACHE_DIR / "images"
AUDIO_CACHE_DIR = CACHE_DIR / "audio"

for d in (DATA_DIR, CACHE_DIR, IMAGE_CACHE_DIR, AUDIO_CACHE_DIR):
    d.mkdir(parents=True, exist_ok=True)

ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")
IMAGE_ANALYSIS_EFFORT = os.environ.get("IMAGE_ANALYSIS_EFFORT", "low")
QUERY_EFFORT = os.environ.get("QUERY_EFFORT", "medium")
ROUTING_EFFORT = os.environ.get("ROUTING_EFFORT", "medium")
IMAGE_MAX_DIMENSION = int(os.environ.get("IMAGE_MAX_DIMENSION", "1024"))

WHISPER_MODEL_SIZE = os.environ.get("WHISPER_MODEL_SIZE", "base")
WHISPER_DEVICE = os.environ.get("WHISPER_DEVICE", "cpu")
WHISPER_COMPUTE_TYPE = os.environ.get("WHISPER_COMPUTE_TYPE", "int8")

MEDIA_CONCURRENCY = int(os.environ.get("MEDIA_CONCURRENCY", "4"))
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "3"))


def get_api_key() -> str | None:
    """Read the API key from the environment only. Never hardcode, never log the value."""
    return os.environ.get("ANTHROPIC_API_KEY")


def require_api_key() -> str:
    """Raise a clear, actionable error if the key is missing. Callers must not
    proceed to a network call without this check."""
    key = get_api_key()
    if not key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set.\n"
            "Set it before running preprocessing or query commands:\n"
            "  PowerShell:  $env:ANTHROPIC_API_KEY = \"sk-ant-...\"\n"
            "  Or create a .env file in the project root (see .env.example) with:\n"
            "    ANTHROPIC_API_KEY=sk-ant-...\n"
            "No network calls will be made until this is set."
        )
    return key
