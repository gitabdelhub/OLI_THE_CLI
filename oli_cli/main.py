import typer
import subprocess
from rich.console import Console
from . import config
from . import groq
from . import shell

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
_FIRST_RUN_FLAG = False


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    global _FIRST_RUN_FLAG
    api_key = config.get_api_key()

    if ctx.invoked_subcommand is None:
        if not api_key or not config.CONFIG_FILE.exists():
            console.print(BANNER, style="bold cyan")
            typer.echo("")
            console.print("[bold]Welcome to OLI — your terminal buddy.[/]")
            typer.echo("")
            console.print("1. Get a free API key ([bold cyan]Groq[/], OpenAI, etc.)")
            console.print("2. Link it by typing: [bold]oli configure YOUR_API_KEY[/]")
            console.print("3. Keep using your terminal. If a command fails, call your buddy: [bold]oli[/]")
            console.print("4. Ask for more: [bold]oli explain 5[/] (5 = number of lines you want)")
            return
        _detect_and_explain()


@app.command()
def run(fichier: str):
    """Run a file and capture errors."""
    result = subprocess.run(["python", fichier], capture_output=True, text=True)

    if result.returncode == 0:
        console.print(result.stdout, end="")
        console.print("[bold green]✅ Done (no errors)[/]")
    else:
        console.print(result.stderr, style="red", end="")
        config.save_last_error({
            "commande": f"python {fichier}",
            "stderr": result.stderr,
            "stdout": result.stdout,
        })
        config.save_to_history(result.stderr)
        console.print("\n[bold yellow]💡 Type 'oli' to understand the error[/]")


@app.command()
def explain(n: int = typer.Argument(3, help="Number of lines of explanation")):
    """Explain the last error. Add a number for more detail."""
    erreur = config.load_last_error()
    api_key = config.get_api_key()

    if not erreur:
        console.print("[bold red]No error saved yet.[/]")
        return

    if not api_key:
        console.print("[bold red]Set your API key: oli configure[/]")
        return

    console.print("[bold blue]🤔 Analysing...[/]")
    reponse = groq.expliquer_erreur(
        stderr=erreur["stderr"],
        commande=erreur["commande"],
        api_key=api_key,
        max_lignes=n,
    )
    console.print(reponse)
    console.print(f"\n[dim]More details: oli explain {n + 5}[/]")


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
    console.print("[bold green]✅ OLI is now smart ![/]")
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


def _detect_and_explain():
    cmd = shell.get_last_command()

    if not cmd:
        console.print("[yellow]No command found in history.[/]")
        console.print("Use [bold]oli run <file>[/] to run code directly")
        return

    console.print(f"Last command: [bold]{cmd}[/]")

    result = shell.re_run(cmd)
    if result is None:
        console.print("[yellow]Command timed out. Try a faster command.[/]")
        return
    if result.returncode == 0:
        console.print(result.stdout, end="")
        console.print("[bold green]✅ No error[/]")
        return

    console.print(result.stderr, style="red", end="")
    config.save_last_error({
        "commande": cmd,
        "stderr": result.stderr,
        "stdout": result.stdout,
    })
    config.save_to_history(result.stderr)

    api_key = config.get_api_key()
    if api_key:
        console.print("\n[bold blue]🤔 Translating error...[/]")
        reponse = groq.expliquer_erreur(
            stderr=result.stderr, commande=cmd,
            api_key=api_key, max_lignes=3,
        )
        console.print(reponse)
        console.print(f"\n[dim]Need more details? → [bold]oli explain 8[/]")


if __name__ == "__main__":
    app()
