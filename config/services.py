import os
from dotenv import load_dotenv

load_dotenv()

config = {
    "ollama": {
        "host": os.getenv("LLM_HOST", "http://localhost:11434"),
        "model": os.getenv("LLM_MODEL", "deepseek-r1:8b"),
        "temperature": os.getenv("LLM_TEMPERATURE", 0.7),
    },
    "telegram": {
        "token": os.getenv("TELEGRAM_TOKEN"),
    },
    "openweathermap": {
        "api_key": os.getenv("OPENWEATHERMAP_API_KEY"),
    },
}
