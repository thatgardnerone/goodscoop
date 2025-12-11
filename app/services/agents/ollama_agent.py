import logging

from ollama import AsyncClient
import httpx

from app.services.agents.agent import Agent
from config import config

logger = logging.getLogger(__name__)


class OllamaAgent(Agent):
    def __init__(self):
        host = config("services.ollama.host")
        model = config("services.ollama.model")
        logger.info(f"Connecting to {host} using model {model}")

        # Get request to host and assert response is 200, "Ollama is running"
        response = httpx.get(host)
        response.raise_for_status()
        assert response.text == "Ollama is running"
        logger.info("Connected to Ollama")

        self.client = AsyncClient(host=host)

        self.model = config("services.ollama.model")
        self.temperature = config("services.ollama.temperature")

    SYSTEM_PROMPT = """You are GoodScoop, a friendly and witty personal assistant crafting daily updates for Jamie, a close friend.

Your updates draw from multiple sources:
- Local Newcastle news (Chronicle Live) - Jamie lives in Newcastle
- Weather forecast - practical daily info
- Newcastle University news - relevant to Jamie's PhD
- Freeman Hospital/NHS news - Jamie's wife works there as a paeds ICU nurse
- Tech and AI news - Jamie's interest area
- Calendar events and bank holidays
- Historical "on this day" facts
- UK and world news

Your tone is casual, warm, and playful. Make messages feel human and enjoyable - like a friend giving a quick catch-up over coffee. Be concise but informative."""

    async def chat(self, message: str) -> str:
        response = await self.client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ],
            tools=None,
            stream=False,
            options={"temperature": self.temperature},
        )

        reply = response["message"]["content"]

        reply = reply.strip('\'"')

        return reply
