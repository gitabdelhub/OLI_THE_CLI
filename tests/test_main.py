from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile

from typer.testing import CliRunner

from oli_cli.main import app, _re_run, get_last_shell_command


runner = CliRunner()


def test_banner_and_welcome_no_config():
    with tempfile.TemporaryDirectory() as tmp:
        with patch("oli_cli.config.OLI_DIR", Path(tmp)):
            with patch("oli_cli.config.CONFIG_FILE", Path(tmp) / "config.json"):
                result = runner.invoke(app, [])
                assert "Welcome to OLI" in result.stdout
                assert "oli configure YOUR_API_KEY" in result.stdout


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout


@patch("oli_cli.main.subprocess.run")
def test_run_success(mock_run):
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Hello World\n"
    mock_run.return_value = mock_result

    result = runner.invoke(app, ["run", "test.py"])
    assert result.exit_code == 0
    assert "Hello World" in result.stdout


@patch("oli_cli.main.subprocess.run")
def test_run_error(mock_run):
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stderr = "NameError: name 'x' is not defined\n"
    mock_run.return_value = mock_result

    with tempfile.TemporaryDirectory() as tmp:
        with patch("oli_cli.config.OLI_DIR", Path(tmp)):
            with patch("oli_cli.config.LAST_ERROR_FILE", Path(tmp) / "last_error.json"):
                result = runner.invoke(app, ["run", "fail.py"])

    assert "NameError" in result.stdout


@patch("oli_cli.main.subprocess.run")
def test_re_run_success(mock_run):
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "ok"
    mock_run.return_value = mock_result

    result = _re_run("echo hello")
    assert result.returncode == 0


@patch("oli_cli.main.subprocess.run")
def test_re_run_timeout(mock_run):
    import subprocess
    mock_run.side_effect = subprocess.TimeoutExpired(cmd="sleep 10", timeout=5)

    result = _re_run("sleep 10")
    assert result is None


@patch("oli_cli.main.subprocess.run")
def test_get_last_shell_command_windows(mock_run):
    mock_result = MagicMock()
    mock_result.stdout = "python test.py\n"
    mock_run.return_value = mock_result

    with patch("sys.platform", "win32"):
        cmd = get_last_shell_command()
        assert cmd == "python test.py"
