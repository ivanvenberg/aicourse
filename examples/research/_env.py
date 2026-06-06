"""Load API keys from environment. Never hardcode secrets."""
import os
from pathlib import Path


def load_dotenv():
    """Best-effort load .env from repo root or examples/research."""
    for candidate in (
        Path(__file__).resolve().parents[2] / ".env",
        Path(__file__).resolve().parent / ".env",
    ):
        if not candidate.exists():
            continue
        for line in candidate.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def require_key(name: str) -> str:
    load_dotenv()
    value = os.environ.get(name)
    if not value:
        raise SystemExit(
            f"Нет {name}. Скопируй docs/env.example → .env и вставь ключ."
        )
    return value


OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
