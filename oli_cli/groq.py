import requests

from . import config


def expliquer_erreur(stderr: str, commande: str, api_key: str, max_lignes: int = 3) -> str:
    api_url = config.get_api_url()
    model = config.get_model()

    prompt = f"""Command: {commande}
Error:
```
{stderr}
```

Explain this error in {max_lignes} sentences max.
Format: "What happened → why → how to fix it".
Be direct, no fluff."""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": f"Answer in {max_lignes} sentences max. Direct, no fluff.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": max_lignes * 80,
    }

    try:
        reponse = requests.post(api_url, headers=headers, json=data, timeout=30)
        reponse.raise_for_status()
        return reponse.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"API error: {e}"
