import subprocess
import sys


def get_last_command() -> str | None:
    """Récupère la dernière commande tapée (avant 'oli')."""
    if sys.platform == "win32":
        return _last_command_powershell()
    return _last_command_posix()


def _last_command_powershell() -> str | None:
    try:
        result = subprocess.run(
            [
                "powershell", "-NoProfile", "-Command",
                "Get-Content (Get-PSReadlineOption).HistorySavePath "
                "| Where-Object { $_ -notmatch '^oli\\b' } "
                "| Select-Object -Last 1"
            ],
            capture_output=True, text=True, timeout=5,
        )
        cmd = result.stdout.strip()
        return cmd if cmd else None
    except Exception:
        return None


def _last_command_posix() -> str | None:
    try:
        result = subprocess.run(
            ["bash", "-c", "history | tail -2 | head -1 | sed 's/^ *[0-9]* *//'"],
            capture_output=True, text=True, timeout=5,
        )
        cmd = result.stdout.strip()
        return cmd if cmd else None
    except Exception:
        return None


def re_run(command: str) -> subprocess.CompletedProcess | None:
    """Re-exécute une commande et capture stdout/stderr."""
    try:
        return subprocess.run(
            command, capture_output=True, text=True, shell=True,
            timeout=15,
        )
    except subprocess.TimeoutExpired:
        return None
