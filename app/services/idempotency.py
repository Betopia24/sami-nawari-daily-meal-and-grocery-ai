from typing import Awaitable, Callable


class IdempotencyService:
    def __init__(self, cache, ttl_seconds: int = 3600) -> None:
        self._cache=cache; self._ttl=ttl_seconds

    async def execute(self, *, scope: str, user_id: str, key: str | None, factory: Callable[[], Awaitable[dict]]) -> tuple[dict,bool]:
        if not key:
            return await factory(), False
        cache_key=f'idempotency:{scope}:{user_id}:{key}'
        cached=await self._cache.get_json(cache_key)
        if cached is not None:
            return cached, True
        result=await factory()
        await self._cache.set_json(cache_key,result,self._ttl)
        return result, False
