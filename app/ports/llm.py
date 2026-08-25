from typing import Protocol
from app.domain.models import (
    UserAIProfile, Recipe, MealPlanDraft, NutritionFacts, NutritionInsight,
    SellerFoodDraft, GeneratedRecipeDraft, ReplacementIntent,
)


class LLMProvider(Protocol):
    @property
    def model_name(self) -> str: ...

    async def generate_meal_plan(
        self,
        *,
        profile: UserAIProfile,
        candidates: list[Recipe],
        start_date: str,
        days: int,
        meals_per_day: list[str],
        goal: str | None,
    ) -> MealPlanDraft: ...

    async def interpret_replacement(self, preference: str) -> ReplacementIntent: ...

    async def generate_nutrition_insight(
        self, *, profile: UserAIProfile, nutrition: NutritionFacts
    ) -> NutritionInsight: ...

    async def generate_seller_recipe(
        self, *, food: SellerFoodDraft, language: str
    ) -> GeneratedRecipeDraft: ...

    async def regenerate_seller_recipe(
        self, *, food: SellerFoodDraft, previous: GeneratedRecipeDraft, instructions: str
    ) -> GeneratedRecipeDraft: ...
