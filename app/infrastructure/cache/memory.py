import asyncio
import time
from copy import deepcopy


class MemoryCache:
    def __init__(self) -> None:
        self._data: dict[str, tuple[float, object]] = {}
        self._lock = asyncio.Lock()

    async def get_json(self, key: str):
        async with self._lock:
            item = self._data.get(key)
            if not item:
                return None
            expires_at, value = item
            if expires_at and expires_at < time.monotonic():
                self._data.pop(key, None)
                return None
            return deepcopy(value)

    async def set_json(self, key: str, value, ttl_seconds: int) -> None:
        expires = time.monotonic() + ttl_seconds if ttl_seconds > 0 else 0
        async with self._lock:
            self._data[key] = (expires, deepcopy(value))

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._data.pop(key, None)

    async def ping(self) -> bool:
        return True


    async def increment(self, key: str, ttl_seconds: int) -> int:
        async with self._lock:
            now=time.monotonic(); item=self._data.get(key)
            if not item or (item[0] and item[0] < now):
                self._data[key]=(now+ttl_seconds,1)
                return 1
            expires,value=item
            value=int(value)+1
            self._data[key]=(expires,value)
            return value
