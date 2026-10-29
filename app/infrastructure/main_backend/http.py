from uuid import UUID
import httpx
from app.core.errors import ProfileNotFound, ResourceNotFound, Forbidden
from app.domain.models import UserAIProfile, FoodItem, Recipe, StoredMealPlan, SellerFoodDraft


class HttpMainBackendClient:
    def __init__(self, base_url: str, timeout_seconds: float = 5.0) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip('/'),
            timeout=timeout_seconds,
        )

    async def _get(self, path: str, *, params: dict | None = None):
        response = await self._client.get(path, params=params)
        if response.status_code == 403:
            raise Forbidden()
        if response.status_code == 404:
            raise ResourceNotFound()
        response.raise_for_status()
        payload = response.json()
        return payload.get('data', payload)

    async def get_ai_profile(self, user_id: UUID) -> UserAIProfile:
        try:
            data = await self._get(f'/internal/ai/users/{user_id}/profile')
        except ResourceNotFound as exc:
            raise ProfileNotFound() from exc
        return UserAIProfile.model_validate(data)

    async def list_food_candidates(self, user_id: UUID, limit: int, meal_type: str | None = None) -> list[FoodItem]:
        data = await self._get('/internal/ai/foods/candidates', params={'user_id': str(user_id), 'limit': limit, 'meal_type': meal_type})
        return [FoodItem.model_validate(x) for x in data]

    async def list_recipe_candidates(self, user_id: UUID, limit: int, meal_type: str | None = None) -> list[Recipe]:
        data = await self._get('/internal/ai/recipes/candidates', params={'user_id': str(user_id), 'limit': limit, 'meal_type': meal_type})
        return [Recipe.model_validate(x) for x in data]

    async def get_food(self, food_id: str) -> FoodItem:
        return FoodItem.model_validate(await self._get(f'/internal/ai/foods/{food_id}'))

    async def get_recipe(self, recipe_id: str) -> Recipe:
        return Recipe.model_validate(await self._get(f'/internal/ai/recipes/{recipe_id}'))

    async def get_meal_plan(self, plan_id: str, user_id: UUID) -> StoredMealPlan:
        return StoredMealPlan.model_validate(await self._get(f'/internal/ai/meal-plans/{plan_id}', params={'user_id': str(user_id)}))

    async def get_seller_food_draft(self, food_id: str, seller_user_id: UUID) -> SellerFoodDraft:
        return SellerFoodDraft.model_validate(await self._get(f'/internal/ai/seller-foods/{food_id}/draft', params={'seller_user_id': str(seller_user_id)}))

    async def close(self) -> None:
        await self._client.aclose()
