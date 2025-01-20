from ollama import AsyncClient
import httpx

from app.services.agents.agent import Agent
from config import config


class OllamaAgent(Agent):
    def __init__(self):
        host = config("services.ollama.host")
        model = config("services.ollama.model")
        print(f"Connecting to {host} using model {model}")

        # Get request to host and assert response is 200, "Ollama is running"
        response = httpx.get(host)
        response.raise_for_status()
        assert response.text == "Ollama is running"
        print("Connected to Agent\n")

        self.client = AsyncClient(host=host)

        self.model = config("services.ollama.model")
        self.temperature = config("services.ollama.temperature")

    async def chat(self, message: str) -> str:
        response = await self.client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a friendly, witty, and engaging news presenter crafting personalised daily updates for a close friend. Your tone is casual, warm, and playful. Prioritise making your messages feel human, thoughtful, and enjoyable to read."},
                {"role": "user", "content": message}
            ],
            tools=None,
            stream=False,
            options={"temperature": self.temperature},
        )

        reply = response["message"]["content"]

        reply = reply.strip('\'"')

        return reply
