from abc import ABC, abstractmethod


class Agent(ABC):
    @abstractmethod
    def chat(self, message: str) -> str:
        pass
