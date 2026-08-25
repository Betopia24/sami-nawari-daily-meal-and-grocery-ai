from typing import Protocol
from uuid import UUID
from app.domain.enums import GenerationFeature


class GenerationRepository(Protocol):
    async def create(
        self, *, generation_id: str, user_id: UUID, feature: GenerationFeature,
        model: str, prompt_version: str, status: str, metadata: dict
    ) -> None: ...
    async def get_output(self, generation_id: str) -> dict | None: ...
    async def save_output(self, generation_id: str, output: dict, status: str = 'completed') -> None: ...
    async def get_latest_output(self, *, user_id: UUID, feature: GenerationFeature, metadata_match: dict) -> tuple[str, dict] | None: ...


class RecommendationEventRepository(Protocol):
    async def add(self, *, user_id: UUID, recommendation_id: str, item_type: str, item_id: str, event: str) -> None: ...


class HealthRepository(Protocol):
    async def ping(self) -> bool: ...
