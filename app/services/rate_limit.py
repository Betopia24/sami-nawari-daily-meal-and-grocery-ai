from app.core.errors import RateLimited


class RateLimiterService:
    def __init__(self, cache, limit_per_minute: int) -> None:
        self._cache=cache
        self._limit=limit_per_minute

    async def check(self, *, user_id: str, feature: str) -> None:
        count=await self._cache.increment(f'ratelimit:{feature}:{user_id}',60)
        if count > self._limit:
            raise RateLimited()
