from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile

from oli_cli import config
from oli_cli import groq


def _setup_config(tmp_dir, api_key="test-key"):
    config.OLI_DIR = Path(tmp_dir)
    config.CONFIG_FILE = Path(tmp_dir) / "config.json"
    config.CONFIG_FILE.write_text(
        f'{{"api_key": "{api_key}", "api_url": "https://api.groq.com/openai/v1/chat/completions", "model": "llama-3.1-8b-instant"}}'
    )


@patch("oli_cli.groq.requests.post")
def test_expliquer_erreur_success(mock_post):
    with tempfile.TemporaryDirectory() as tmp:
        _setup_config(tmp)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "This is a division by zero error."}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = groq.expliquer_erreur(
            stderr="ZeroDivisionError: division by zero",
            commande="python test.py",
            max_lignes=3,
        )
        assert "division by zero" in result
        mock_post.assert_called_once()


@patch("oli_cli.groq.requests.post")
def test_expliquer_commande(mock_post):
    with tempfile.TemporaryDirectory() as tmp:
        _setup_config(tmp)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "This command runs docker containers."}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = groq.expliquer_commande("docker compose up")
        assert "docker" in result.lower() or "container" in result.lower()


@patch("oli_cli.groq.requests.post")
def test_ask_question(mock_post):
    with tempfile.TemporaryDirectory() as tmp:
        _setup_config(tmp)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Jenkins is a CI/CD tool."}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = groq.ask_question("what is jenkins?")
        assert "jenkins" in result.lower() or "ci/cd" in result.lower()


@patch("oli_cli.groq.requests.post")
def test_api_error_handling(mock_post):
    with tempfile.TemporaryDirectory() as tmp:
        _setup_config(tmp)
        from requests.exceptions import RequestException

        mock_post.side_effect = RequestException("Connection failed")

        result = groq.expliquer_erreur(
            stderr="error",
            commande="python test.py",
        )
        assert "API error" in result
