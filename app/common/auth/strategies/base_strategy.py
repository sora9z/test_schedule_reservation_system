from abc import ABC, abstractmethod

from fastapi import Request


class AuthStrategy(ABC):
    @abstractmethod
    async def authenticate(self, request: Request) -> dict:
        pass
