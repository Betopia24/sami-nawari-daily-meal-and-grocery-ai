from uuid import UUID
from app.domain.models import UserAIProfile


class AIProfileService:
    def __init__(self, main_backend, cache, ttl_seconds: int = 900) -> None:
        self._main=main_backend; self._cache=cache; self._ttl=ttl_seconds

    @staticmethod
    def _key(user_id: UUID) -> str:
        return f'ai:profile:{user_id}'

    async def get(self, user_id: UUID) -> UserAIProfile:
        cached=await self._cache.get_json(self._key(user_id))
        if cached:
            return UserAIProfile.model_validate(cached)
        profile=await self._main.get_ai_profile(user_id)
        await self._cache.set_json(self._key(user_id), profile.model_dump(mode='json'), self._ttl)
        return profile

    async def invalidate(self, user_id: UUID) -> None:
        await self._cache.delete(self._key(user_id))
