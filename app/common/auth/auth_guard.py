from fastapi import Request

from app.common.auth.strategies.base_strategy import AuthStrategy


class AuthGuard:
    def __init__(self, strategy: AuthStrategy):
        self.strategy = strategy

    async def authenticate(self, request: Request) -> dict:
        return await self.strategy.authenticate(request)
