import json
from app.core.errors import GenerationFailed
from app.domain.models import (
    UserAIProfile, Recipe, MealPlanDraft, NutritionFacts, NutritionInsight,
    SellerFoodDraft, GeneratedRecipeDraft, ReplacementIntent,
)


class OpenAILLMProvider:
    """OpenAI Responses API adapter.

    Uses structured Pydantic outputs through responses.parse. The model is configured
    via OPENAI_MODEL so production can switch models without changing business code.
    """
    def __init__(self, *, api_key: str, model: str, timeout_seconds: float = 45, max_retries: int = 2) -> None:
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError('Install openai dependency for production') from exc
        self._client = AsyncOpenAI(api_key=api_key, timeout=timeout_seconds, max_retries=max_retries)
        self._model = model

    @property
    def model_name(self) -> str:
        return self._model

    async def _parse(self, *, system: str, user_payload: dict, output_model):
        try:
            response = await self._client.responses.parse(
                model=self._model,
                input=[
                    {'role': 'system', 'content': system},
                    {'role': 'user', 'content': json.dumps(user_payload, default=str)},
                ],
                text_format=output_model,
            )
            parsed = response.output_parsed
            if parsed is None:
                raise GenerationFailed('OpenAI returned no structured output')
            return parsed
        except GenerationFailed:
            raise
        except Exception as exc:  # pragma: no cover - external API
            raise GenerationFailed(f'OpenAI request failed: {type(exc).__name__}') from exc

    async def generate_meal_plan(self, *, profile: UserAIProfile, candidates: list[Recipe], start_date: str, days: int, meals_per_day: list[str], goal: str | None) -> MealPlanDraft:
        system = (
            'You create practical wellness-oriented meal plans. Select ONLY recipe_id values from the supplied candidates. '
            'Never introduce a recipe not in the candidate list. Respect dietary and allergy constraints already reflected in candidates. '
            'Return exactly the requested date range and meal types. Do not provide medical diagnosis or treatment.'
        )
        payload={
            'profile': profile.model_dump(mode='json'), 'start_date': start_date, 'days': days,
            'meals_per_day': meals_per_day, 'goal': goal,
            'candidates': [r.model_dump(mode='json') for r in candidates],
        }
        return await self._parse(system=system,user_payload=payload,output_model=MealPlanDraft)

    async def interpret_replacement(self, preference: str) -> ReplacementIntent:
        return await self._parse(
            system='Extract replacement intent. Do not invent user allergies or dietary preferences.',
            user_payload={'preference': preference}, output_model=ReplacementIntent,
        )

    async def generate_nutrition_insight(self, *, profile: UserAIProfile, nutrition: NutritionFacts) -> NutritionInsight:
        system=(
            'Explain ONLY the supplied calculated nutrition values in plain, non-medical wellness language. '
            'Do not recalculate values, diagnose conditions, prescribe treatment, or make unsupported health claims.'
        )
        return await self._parse(
            system=system,
            user_payload={'profile_goal': profile.nutrition_goal, 'nutrition': nutrition.model_dump()},
            output_model=NutritionInsight,
        )

    async def generate_seller_recipe(self, *, food: SellerFoodDraft, language: str) -> GeneratedRecipeDraft:
        system=(
            'Create an editable recipe draft from seller-provided food data. Every required ingredient MUST use an ingredient_id '
            'from the supplied ingredient list. Never silently introduce a new required ingredient. If something seems missing, put it '
            'only in suggested_missing_ingredients. Preserve seller times and servings unless the data is contradictory. '
            f'Write the recipe in language code {language}.'
        )
        return await self._parse(system=system,user_payload=food.model_dump(mode='json'),output_model=GeneratedRecipeDraft)

    async def regenerate_seller_recipe(self, *, food: SellerFoodDraft, previous: GeneratedRecipeDraft, instructions: str) -> GeneratedRecipeDraft:
        system=(
            'Revise the recipe draft using the seller instruction. Required ingredients may only use IDs from seller food data. '
            'Do not add unapproved required ingredients.'
        )
        return await self._parse(
            system=system,
            user_payload={'food': food.model_dump(mode='json'),'previous': previous.model_dump(mode='json'),'instructions': instructions},
            output_model=GeneratedRecipeDraft,
        )
