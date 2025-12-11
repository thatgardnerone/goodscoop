# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GoodScoop is a Python application that delivers personalized, AI-summarized news updates to users via Telegram. It fetches news from Google News, summarizes it using an LLM (Ollama with DeepSeek R1), and sends friendly, conversational messages to subscribers.

## Commands

```bash
# Install dependencies (requires Poetry and Python 3.13+)
poetry install

# Run the application (starts Telegram bot)
poetry run goodscoop
# or: poetry run python main.py

# Run linter
poetry run ruff check .

# Run tests
poetry run pytest

# Ensure Ollama is running before starting
# Default host: http://tgoml.netbird.selfhosted:11434
```

## Architecture

### Entry Point
- `main.py` - Initializes the agent and defines `create_message()` which generates personalized news summaries. Starts the Telegram bot via `Notifications.run()`.

### Core Components

**Config System** (`config/`)
- `__init__.py` - Singleton config loader with dot-notation access (e.g., `config("services.ollama.host")`)
- `app.py` - User settings (name from env)
- `services.py` - External service configs (Ollama, Telegram)

**Agents** (`app/services/agents/`)
- `agent.py` - Abstract base class defining the `chat()` interface
- `ollama_agent.py` - Ollama implementation using AsyncClient (currently active)
- `openai_agent.py` - Empty placeholder for OpenAI implementation

**Services** (`app/services/`)
- `notifications.py` - Telegram bot with APScheduler for random daily message delivery

**Models** (`app/models/`)
- `news.py` - Fetches top UK news from Google News with 1-hour LRU caching

### Data Flow
1. User subscribes via Telegram `/start` command
2. Scheduler triggers `send_message()` at random daily times
3. `create_message()` fetches news and builds prompt with current datetime context
4. Ollama agent summarizes news in a friendly tone
5. Response is parsed (strips `</think>` tags from DeepSeek R1 output) and sent via Telegram

## Environment Variables

Required in `.env` (see `.env.example`):
- `OLLAMA_HOST` - Ollama server URL
- `OLLAMA_MODEL` - Model name (default: `deepseek-r1:8b`)
- `TELEGRAM_TOKEN` - Telegram bot token
- `USER_NAME` - Recipient's name for personalization
