import json


class RedisCache:
    def __init__(self, url: str) -> None:
        try:
            from redis.asyncio import Redis
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError('Install redis dependency for production') from exc
        self._client = Redis.from_url(url, decode_responses=True)

    async def get_json(self, key: str):
        value = await self._client.get(key)
        return json.loads(value) if value else None

    async def set_json(self, key: str, value, ttl_seconds: int) -> None:
        await self._client.set(key, json.dumps(value, default=str), ex=ttl_seconds)

    async def delete(self, key: str) -> None:
        await self._client.delete(key)

    async def ping(self) -> bool:
        return bool(await self._client.ping())

    async def close(self) -> None:
        await self._client.aclose()


    async def increment(self, key: str, ttl_seconds: int) -> int:
        value = await self._client.incr(key)
        if value == 1:
            await self._client.expire(key, ttl_seconds)
        return int(value)
