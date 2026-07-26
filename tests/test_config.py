import json
import tempfile
from pathlib import Path

from oli_cli import config


def test_save_and_load_config():
    with tempfile.TemporaryDirectory() as tmp:
        config.OLI_DIR = Path(tmp)
        config.CONFIG_FILE = Path(tmp) / "config.json"

        config.save_config({"api_key": "test-key"})
        assert config.CONFIG_FILE.exists()

        loaded = config.load_config()
        assert loaded["api_key"] == "test-key"


def test_get_api_key():
    with tempfile.TemporaryDirectory() as tmp:
        config.OLI_DIR = Path(tmp)
        config.CONFIG_FILE = Path(tmp) / "config.json"

        config.save_config({"api_key": "my-key"})
        assert config.get_api_key() == "my-key"


def test_get_api_key_empty():
    with tempfile.TemporaryDirectory() as tmp:
        config.OLI_DIR = Path(tmp)
        config.CONFIG_FILE = Path(tmp) / "config.json"

        config.CONFIG_FILE.write_text("{}")
        assert config.get_api_key() == ""


def test_get_api_url_default():
    with tempfile.TemporaryDirectory() as tmp:
        config.OLI_DIR = Path(tmp)
        config.CONFIG_FILE = Path(tmp) / "config.json"

        config.CONFIG_FILE.write_text("{}")
        assert "groq.com" in config.get_api_url()


def test_save_last_error_and_load():
    with tempfile.TemporaryDirectory() as tmp:
        config.OLI_DIR = Path(tmp)
        config.LAST_ERROR_FILE = Path(tmp) / "last_error.json"

        config.save_last_error({"stderr": "test error", "commande": "python x.py"})
        loaded = config.load_last_error()
        assert loaded["stderr"] == "test error"
        assert loaded["commande"] == "python x.py"


def test_load_last_error_none():
    with tempfile.TemporaryDirectory() as tmp:
        config.OLI_DIR = Path(tmp)
        config.LAST_ERROR_FILE = Path(tmp) / "last_error.json"

        assert config.load_last_error() is None


def test_save_to_history():
    with tempfile.TemporaryDirectory() as tmp:
        config.OLI_DIR = Path(tmp)
        config.HISTORY_FILE = Path(tmp) / "history.json"

        config.save_to_history("error 1")
        config.save_to_history("error 2")
        history = config.load_history()
        assert len(history) == 2
        assert history[0] == "error 1"
        assert history[1] == "error 2"


def test_history_max_size():
    with tempfile.TemporaryDirectory() as tmp:
        config.OLI_DIR = Path(tmp)
        config.HISTORY_FILE = Path(tmp) / "history.json"

        for i in range(60):
            config.save_to_history(f"error {i}")
        history = config.load_history()
        assert len(history) == 50
