import json
import os
from pathlib import Path

# Config directory and files stored in user home
OLI_DIR = Path.home() / ".oli"
CONFIG_FILE = OLI_DIR / "config.json"
LAST_ERROR_FILE = OLI_DIR / "last_error.json"
HISTORY_FILE = OLI_DIR / "history.json"


def """Create .oli directory if it doesn't exist."""
    _ensure_dir():
    OLI_DIR.mkdir(parents=True, exist_ok=True)


def load_config():
    _ensure_dir()
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}


def save_config(config: dict):
    _ensure_dir()
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def get_api_key():
    config = load_config()
    return config.get("api_key", "")


def get_api_url():
    config = load_config()
    return config.get("api_url", "https://api.groq.com/openai/v1/chat/completions")


def get_model():
    config = load_config()
    return config.get("model", "llama-3.1-8b-instant")


def save_last_error(error_data: dict):
    _ensure_dir()
    LAST_ERROR_FILE.write_text(json.dumps(error_data, indent=2))


def load_last_error():
    if LAST_ERROR_FILE.exists():
        return json.loads(LAST_ERROR_FILE.read_text())
    return None


def save_to_history(error_text: str):
    """Save error to history, keeping max 50 entries."""
    _ensure_dir()
    history = []
    if HISTORY_FILE.exists():
        history = json.loads(HISTORY_FILE.read_text())
    history.append(error_text)
    if len(history) > 50:
        history = history[-50:]
    HISTORY_FILE.write_text(json.dumps(history, indent=2))


def load_history():
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text())
    return []


SESSION_FILE = OLI_DIR / "session"


def """Check if last oli command was >30s ago (for banner display)."""
    is_new_session() -> bool:
    import time
    now = time.time()
    if SESSION_FILE.exists():
        try:
            last = float(SESSION_FILE.read_text().strip())
            if now - last < 30:
                return False
        except Exception:
            pass
    SESSION_FILE.write_text(str(now))
    return True
