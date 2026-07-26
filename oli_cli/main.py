import typer
import subprocess
from pathlib import Path
from rich.console import Console

from . import config
from . import groq

BANNER = r"""
  ___  _     ___ 
 / _ \| |   |_ _|
| | | | |    | | 
| |_| | |___ | | 
 \___/|_____|___|
by Abdallah_LE
"""

app = typer.Typer()
console = Console()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Main entry point - show banner or detect last error."""
    if config.is_new_session():
        console.print(BANNER, style="bold cyan")

    if ctx.invoked_subcommand is None:
        if not config.get_api_key() or not config.CONFIG_FILE.exists():
            typer.echo("")
            console.print("[bold]Welcome to OLI — your terminal buddy.[/]")
            typer.echo("")
            console.print("1. Get a free API key ([bold cyan]Groq[/], OpenAI, etc.)")
            console.print("2. Link it: [bold]oli configure YOUR_API_KEY[/]")
            console.print("3. If a command fails, call your buddy: [bold]oli[/]")
            console.print("4. See all commands: [bold]oli more[/]")
            return
        _detect_and_explain()


LANG_MAP = {
    ".py": ["python"],
    ".js": ["node"],
    ".ts": ["npx", "ts-node"],
    ".go": ["go", "run"],
    ".rb": ["ruby"],
    ".sh": ["bash"],
    ".php": ["php"],
    ".rs": ["rustc"],
    ".java": ["javac"],
}


def _detect_lang(fichier: str) -> list[str] | None:
    ext = Path(fichier).suffix
    cmd = LANG_MAP.get(ext)
    if cmd:
        if ext in (".py", ".js", ".rb", ".sh", ".php"):
            return [*cmd, fichier]
        if ext == ".ts":
            return [*cmd, fichier]
        if ext == ".go":
            return [*cmd, fichier]
        if ext == ".rs":
            return [*cmd, fichier]
    return None


@app.command()
def run(fichier: str):
    """Run a file and capture errors."""
    lang_cmd = _detect_lang(fichier)
    if lang_cmd is None:
        console.print(f"[yellow]Unsupported file: {fichier}[/]")
        console.print("Supported: .py .js .ts .go .rb .sh .php .rs .java")
        return

    result = subprocess.run(lang_cmd, capture_output=True, text=True)

    if result.returncode == 0:
        console.print(result.stdout, end="")
        console.print("[bold green]Done (no errors)[/]")
    else:
        console.print(result.stderr, style="red", end="")
        config.save_last_error({
            "commande": " ".join(lang_cmd),
            "stderr": result.stderr,
            "stdout": result.stdout,
        })
        config.save_to_history(result.stderr)
        console.print("\n[bold yellow]Type 'oli' to understand the error[/]")


@app.command()
def explain(n: int = typer.Argument(3, help="Number of lines")):
    """Explain the last error."""
    erreur = config.load_last_error()
    if not erreur:
        console.print("[bold red]No error saved yet.[/]")
        return
    if not config.get_api_key():
        console.print("[bold red]Set your API key: oli configure[/]")
        return

    console.print("[bold blue]Analysing...[/]")
    reponse = groq.expliquer_erreur(erreur["stderr"], erreur["commande"], max_lignes=n)
    console.print(reponse)
    console.print(f"\n[dim]More: oli explain {n + 5}[/]")


@app.command()
def whatis(commande: str = typer.Argument(..., help="Command to explain")):
    """Explain what a command does before running it."""
    if not config.get_api_key():
        console.print("[bold red]Set your API key: oli configure[/]")
        return

    console.print(f"[bold blue]What is [bold]{commande}[/]?[/]")
    reponse = groq.expliquer_commande(commande)
    console.print(reponse)


@app.command()
def ask(question: str = typer.Argument(..., help="Your question")):
    """Ask anything to OLI."""
    if not config.get_api_key():
        console.print("[bold red]Set your API key: oli configure[/]")
        return

    console.print("[bold blue]Thinking...[/]")
    reponse = groq.ask_question(question)
    console.print(reponse)


@app.command()
def chat():
    """Start an interactive chat with OLI."""
    if not config.get_api_key():
        console.print("[bold red]Set your API key: oli configure[/]")
        return

    console.print("[bold cyan]Chat mode — type 'exit' to stop[/]")
    history = [{"role": "system", "content": "You are OLI, a terminal buddy. Be concise and helpful."}]

    while True:
        user_input = typer.prompt("You")
        if user_input.lower() in ("exit", "quit"):
            break

        history.append({"role": "user", "content": user_input})
        reponse = groq._ask(history)
        console.print(f"[bold cyan]OLI[/] {reponse}")
        history.append({"role": "assistant", "content": reponse})


@app.command()
def configure(
    api_key: str = typer.Argument(None, help="Your API key"),
    api_url: str = typer.Option("https://api.groq.com/openai/v1/chat/completions", "--url", help="API endpoint URL"),
    model: str = typer.Option("llama-3.1-8b-instant", "--model", "-m", help="Model name"),
):
    """Set your API key and provider."""
    if not api_key:
        console.print("Get a free key from [bold cyan]https://console.groq.com[/]")
        api_key = typer.prompt("Paste your key here")
    config.save_config({"api_key": api_key, "api_url": api_url, "model": model})
    console.print("[bold green]OLI is now smart ![/]")
    console.print("Run a command that fails, then type [bold]oli[/]")


@app.command()
def historique():
    """Show recent error history."""
    entries = config.load_history()
    if not entries:
        console.print("[yellow]No history yet.[/]")
        return

    for i, entry in enumerate(entries[-5:], 1):
        console.print(f"\n[bold cyan]--- Error {i} ---[/]")
        console.print(entry[:300])


@app.command()
def more():
    """Show all OLI commands."""
    console.print("[bold]Available commands:[/]")
    console.print("  [bold]oli[/]            → Detect last error and explain")
    console.print("  [bold]oli run <file>[/] → Run a file (.py .js .ts .go .rb .sh .php)")
    console.print("  [bold]oli explain [N][/] → More details (N = lines)")
    console.print("  [bold]oli whatis <cmd>[/] → Explain a command before running")
    console.print("  [bold]oli ask <question>[/] → Ask anything")
    console.print("  [bold]oli chat[/]        → Chat mode")
    console.print("  [bold]oli configure KEY[/] → Set your API key")
    console.print("  [bold]oli historique[/]  → Show error history")
    console.print("  [bold]oli more[/]        → Show this list")


def _detect_and_explain():
    cmd = get_last_shell_command()

    if not cmd:
        console.print("[yellow]No command found in history.[/]")
        console.print("Use [bold]oli run <file>[/] to run code directly")
        return

    console.print(f"Last command: [bold]{cmd}[/]")

    result = _re_run(cmd)
    if result is None:
        console.print("[yellow]Command timed out.[/]")
        return
    if result.returncode == 0:
        console.print(result.stdout, end="")
        console.print("[bold green]No error[/]")
        return

    console.print(result.stderr, style="red", end="")
    config.save_last_error({
        "commande": cmd,
        "stderr": result.stderr,
        "stdout": result.stdout,
    })
    config.save_to_history(result.stderr)

    if config.get_api_key():
        console.print("\n[bold blue]Translating error...[/]")
        reponse = groq.expliquer_erreur(result.stderr, cmd, max_lignes=3)
        console.print(reponse)
        console.print("[dim]More: [bold]oli explain 8[/]")


def get_last_shell_command() -> str | None:
    """Get last command from shell history (PowerShell or bash)."""
    import sys
    try:
        if sys.platform == "win32":
            r = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 "Get-Content (Get-PSReadlineOption).HistorySavePath "
                 "| Where-Object { $_ -notmatch '^oli\\b' } "
                 "| Select-Object -Last 1"],
                capture_output=True, text=True, timeout=5,
            )
        else:
            r = subprocess.run(
                ["bash", "-c", "history | tail -1 | sed 's/^ *[0-9]* *//'"],
                capture_output=True, text=True, timeout=5,
            )
        return r.stdout.strip() or None
    except Exception:
        return None


def _re_run(command: str) -> subprocess.CompletedProcess | None:
    """Re-run command with 15s timeout, return None if timeout."""
    try:
        return subprocess.run(
            command, capture_output=True, text=True, shell=True, timeout=15,
        )
    except subprocess.TimeoutExpired:
        return None


if __name__ == "__main__":
    app()
