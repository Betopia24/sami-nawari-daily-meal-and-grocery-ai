from uuid import UUID
from app.core.errors import ProfileNotFound, ResourceNotFound, Forbidden
from app.domain.models import UserAIProfile, FoodItem, Recipe, StoredMealPlan, SellerFoodDraft


class InMemoryMainBackendClient:
    def __init__(self) -> None:
        self.profiles: dict[UUID, UserAIProfile] = {}
        self.foods: dict[str, FoodItem] = {}
        self.recipes: dict[str, Recipe] = {}
        self.meal_plans: dict[str, StoredMealPlan] = {}
        self.seller_foods: dict[str, SellerFoodDraft] = {}

    async def get_ai_profile(self, user_id: UUID) -> UserAIProfile:
        if user_id not in self.profiles:
            raise ProfileNotFound()
        return self.profiles[user_id]

    async def list_food_candidates(self, user_id: UUID, limit: int, meal_type: str | None = None) -> list[FoodItem]:
        items = [x for x in self.foods.values() if not meal_type or meal_type in x.meal_types]
        return items[:limit]

    async def list_recipe_candidates(self, user_id: UUID, limit: int, meal_type: str | None = None) -> list[Recipe]:
        items = [x for x in self.recipes.values() if not meal_type or meal_type in x.meal_types]
        return items[:limit]

    async def get_food(self, food_id: str) -> FoodItem:
        try: return self.foods[food_id]
        except KeyError as exc: raise ResourceNotFound(f'Food {food_id} not found') from exc

    async def get_recipe(self, recipe_id: str) -> Recipe:
        try: return self.recipes[recipe_id]
        except KeyError as exc: raise ResourceNotFound(f'Recipe {recipe_id} not found') from exc

    async def get_meal_plan(self, plan_id: str, user_id: UUID) -> StoredMealPlan:
        try: plan = self.meal_plans[plan_id]
        except KeyError as exc: raise ResourceNotFound(f'Meal plan {plan_id} not found') from exc
        if plan.user_id != user_id:
            raise Forbidden('Meal plan does not belong to user')
        return plan

    async def get_seller_food_draft(self, food_id: str, seller_user_id: UUID) -> SellerFoodDraft:
        try: food = self.seller_foods[food_id]
        except KeyError as exc: raise ResourceNotFound(f'Seller food {food_id} not found') from exc
        if food.seller_user_id != seller_user_id:
            raise Forbidden('Seller food does not belong to user')
        return food
