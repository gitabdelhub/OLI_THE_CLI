import requests

from . import config


def _ask(messages: list[dict], max_tokens: int = 500) -> str:
    api_url = config.get_api_url()
    model = config.get_model()
    api_key = config.get_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": max_tokens,
    }

    try:
        reponse = requests.post(api_url, headers=headers, json=data, timeout=30)
        reponse.raise_for_status()
        return reponse.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"API error: {e}"


def expliquer_erreur(stderr: str, commande: str, max_lignes: int = 3) -> str:
    """Explain error in max_lignes sentences using LLM."""
    prompt = f"""Command: {commande}
Error:
```
{stderr}
```

Explain this error in {max_lignes} sentences max.
Format: "What happened → why → how to fix it"."""

    return _ask([
        {"role": "system", "content": f"Answer in {max_lignes} sentences max. Direct, no fluff."},
        {"role": "user", "content": prompt},
    ], max_tokens=max_lignes * 80)


def expliquer_commande(commande: str) -> str:
    prompt = f"Explain what this command does in 2-3 sentences:\n{commande}"

    return _ask([
        {"role": "system", "content": "You explain CLI commands briefly. No fluff."},
        {"role": "user", "content": prompt},
    ], max_tokens=200)


def ask_question(question: str) -> str:
    return _ask([
        {"role": "system", "content": "You are OLI, a terminal buddy. Max 5 sentences. Short, no fluff."},
        {"role": "user", "content": question},
    ], max_tokens=200)
