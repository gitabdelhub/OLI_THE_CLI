# OLI — Your Terminal Buddy

OLI catches your errors and explains them in plain English. No more copy-pasting to ChatGPT.

## Quick Start

```bash
pip install oli-cli
oli configure YOUR_API_KEY
# Run any command that fails, then:
oli
```

## Usage

| Command | What it does |
|---------|-------------|
| `oli` | Detect last command, explain if error |
| `oli explain [N]` | Explain with N lines of detail |
| `oli run <file>` | Run a file and capture errors |
| `oli configure KEY` | Set your API key |
| `oli historique` | Show recent error history |

## API Providers

OLI works with any OpenAI-compatible API:

```bash
# Groq (free, default)
oli configure gsk_...

# OpenAI
oli configure sk-... --url https://api.openai.com/v1/chat/completions --model gpt-4o-mini
```

## How it works

1. You run a command → it fails
2. You type `oli` → OLI re-runs it quietly, captures the error
3. OLI sends it to an LLM → explains in 3 sentences
4. Type `oli explain 8` for more detail

## License

MIT
