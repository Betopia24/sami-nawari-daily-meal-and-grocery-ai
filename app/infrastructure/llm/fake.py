from datetime import date, timedelta
from app.domain.models import (
    UserAIProfile, Recipe, MealPlanDraft, MealPlanDay, MealPlanItem,
    NutritionFacts, NutritionInsight, SellerFoodDraft, GeneratedRecipeDraft,
    GeneratedRecipeIngredient, GeneratedRecipeStep, ReplacementIntent,
)


class FakeLLMProvider:
    def __init__(self, model_name: str = 'fake-model') -> None:
        self._model_name = model_name

    @property
    def model_name(self) -> str:
        return self._model_name

    async def generate_meal_plan(self, *, profile: UserAIProfile, candidates: list[Recipe], start_date: str, days: int, meals_per_day: list[str], goal: str | None) -> MealPlanDraft:
        start = date.fromisoformat(start_date)
        if not candidates:
            return MealPlanDraft(days=[])
        result=[]
        idx=0
        for day_num in range(days):
            meals=[]
            for meal_type in meals_per_day:
                matching=[r for r in candidates if not r.meal_types or meal_type in r.meal_types]
                pool=matching or candidates
                recipe=pool[idx % len(pool)]
                idx += 1
                meals.append(MealPlanItem(meal_type=meal_type, recipe_id=recipe.recipe_id, servings=profile.household_size))
            result.append(MealPlanDay(date=start+timedelta(days=day_num), meals=meals))
        return MealPlanDraft(days=result)

    async def interpret_replacement(self, preference: str) -> ReplacementIntent:
        terms=[x.lower() for x in preference.replace(',', ' ').split() if len(x)>2]
        return ReplacementIntent(required_terms=terms[:5])

    async def generate_nutrition_insight(self, *, profile: UserAIProfile, nutrition: NutritionFacts) -> NutritionInsight:
        return NutritionInsight(
            summary=f'This plan averages {nutrition.calories:.0f} calories and {nutrition.protein_g:.0f}g protein per day.',
            positive_points=['Nutrition values are calculated from structured recipe data.'],
            suggestions=['Keep meals varied and adjust portions to your personal needs.'],
        )

    async def generate_seller_recipe(self, *, food: SellerFoodDraft, language: str) -> GeneratedRecipeDraft:
        ingredients=[GeneratedRecipeIngredient(ingredient_id=i.ingredient_id,name=i.name,quantity=i.quantity,unit=i.unit) for i in food.ingredients]
        steps=[
            GeneratedRecipeStep(step_number=1,instruction=food.preparation_notes or 'Prepare all listed ingredients.'),
            GeneratedRecipeStep(step_number=2,instruction=food.cooking_method or 'Cook the ingredients using the seller-provided method until ready.'),
        ]
        return GeneratedRecipeDraft(
            title=food.name, summary=food.details or f'A seller-provided recipe for {food.name}.', servings=food.servings,
            prep_time_minutes=food.prep_time_minutes, cook_time_minutes=food.cook_time_minutes,
            ingredients=ingredients, steps=steps,
        )

    async def regenerate_seller_recipe(self, *, food: SellerFoodDraft, previous: GeneratedRecipeDraft, instructions: str) -> GeneratedRecipeDraft:
        copy=previous.model_copy(deep=True)
        copy.summary=f'{previous.summary} Updated request: {instructions}'
        return copy
