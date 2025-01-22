import os
from dotenv import load_dotenv

load_dotenv()

config = {
    "ollama": {
        "host": os.getenv("OLLAMA_HOST", "http://tgoml.netbird.selfhosted:11434"),
        "model": os.getenv("OLLAMA_MODEL", "deepseek-r1:8b"),
        "temperature": os.getenv("OLLAMA_TEMPERATURE", 0.7),
    },
    "telegram": {
        "token": os.getenv("TELEGRAM_TOKEN"),
    },
}
