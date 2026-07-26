```
  ___  _     ___ 
 / _ \| |   |_ _|
| | | | |    | | 
| |_| | |___ | | 
 \___/|_____|___|
by Abdallah_LE
```

# OLI — Your Terminal Buddy

A funny CLI for debugging, asking about what a command does, or just talking.

## Get Started

1. **Get a free API key** from [Groq](https://console.groq.com), OpenAI, or any provider you like
2. **Link it**: `oli configure YOUR_API_KEY`
3. Keep using your terminal. If a command fails, call your buddy:

```bash
oli
```

Done. No copy-paste, no browser. Your error, explained in plain English.

## Commands

| Command | What it does |
|---------|-------------|
| `oli` | Detect your last command, explain if it failed |
| `oli explain [N]` | More details (N = number of lines) |
| `oli whatis <cmd>` | Explain a command before you run it |
| `oli ask <question>` | Ask anything to OLI |
| `oli chat` | Just talk — interactive mode |
| `oli run <file>` | Run a file and catch errors |
| `oli configure KEY` | Set your API key |

## Any API works

OLI works with **any** OpenAI-compatible provider:

```bash
# Groq (free, default)
oli configure gsk_...

# OpenAI
oli configure sk-... --url https://api.openai.com/v1/chat/completions --model gpt-4o-mini

# Whatever you want
oli configure your_key --url https://your-provider.com/v1 --model your-model
```

## How it works

1. You run a command → it fails
2. You type `oli` → OLI catches it, re-runs it, captures the error
3. Sends it to your LLM → you get a clear explanation
4. Not enough? `oli explain 8`

## License

MIT — do whatever.
