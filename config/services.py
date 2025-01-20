import os
from dotenv import load_dotenv

load_dotenv()

config = {
    "ollama": {
        "host": os.getenv("OLLAMA_HOST", "http://tgoml.netbird.selfhosted:11434"),
        "model": os.getenv("OLLAMA_MODEL", "llama3.3:70b-instruct-q2_K"),
        "temperature": os.getenv("OLLAMA_TEMPERATURE", 0.8),
    },
    "telegram": {
        "token": os.getenv("TELEGRAM_TOKEN"),
    },
}
