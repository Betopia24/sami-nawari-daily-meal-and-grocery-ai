from __future__ import annotations
from typing import Any, Generic, TypeVar
from uuid import UUID
from pydantic import BaseModel, Field
from app.domain.enums import CompatibilityStatus, ResourceType, RecommendationEventType
from app.domain.models import MealPlanDraft, GeneratedRecipeDraft, NutritionFacts, NutritionInsight

T = TypeVar('T')


class Meta(BaseModel):
    cached: bool = False


class APIResponse(BaseModel, Generic[T]):
    request_id: str
    data: T
    meta: Meta = Field(default_factory=Meta)


class FoodRecommendationRequest(BaseModel):
    limit: int = Field(default=20, ge=1, le=50)
    meal_type: str | None = None
    delivery_zone_id: str | None = None
    exclude_food_ids: set[str] = Field(default_factory=set)


class RecipeRecommendationRequest(BaseModel):
    limit: int = Field(default=20, ge=1, le=50)
    meal_type: str | None = None
    max_cooking_time_minutes: int | None = Field(default=None, ge=1, le=600)
    exclude_recipe_ids: set[str] = Field(default_factory=set)


class RecommendationItem(BaseModel):
    item_id: str
    score: float = Field(ge=0, le=1)
    compatibility: CompatibilityStatus
    reasons: list[str] = Field(default_factory=list)


class RecommendationResult(BaseModel):
    recommendation_id: str
    items: list[RecommendationItem]


class MealPlanGenerateRequest(BaseModel):
    start_date: str
    days: int = Field(default=7, ge=1, le=14)
    meals_per_day: list[str] = Field(default_factory=lambda: ['breakfast', 'lunch', 'dinner'])
    goal_override: str | None = None
    excluded_recipe_ids: set[str] = Field(default_factory=set)


class MealPlanGenerateResult(BaseModel):
    generation_id: str
    profile_version: int
    plan: MealPlanDraft


class ReplacementOptionsRequest(BaseModel):
    preference: str = Field(default='', max_length=500)
    limit: int = Field(default=3, ge=1, le=10)


class ReplacementOption(BaseModel):
    recipe_id: str
    compatibility: CompatibilityStatus
    similarity_score: float = Field(ge=0, le=1)
    reason: str | None = None


class ReplacementOptionsResult(BaseModel):
    current_recipe_id: str
    options: list[ReplacementOption]


class NutritionInsightResult(BaseModel):
    generation_id: str
    nutrition: NutritionFacts
    insight: NutritionInsight


class GroceryFromMealPlanRequest(BaseModel):
    meal_plan_id: str


class GroceryFromRecipeRequest(BaseModel):
    recipe_id: str
    servings: int = Field(ge=1, le=50)


class GroceryItem(BaseModel):
    ingredient_id: str
    name: str
    quantity: float
    unit: str
    category: str


class GroceryDraftResult(BaseModel):
    source_type: str
    source_id: str
    items: list[GroceryItem]


class GenerateSellerRecipeRequest(BaseModel):
    language: str = Field(default='en', min_length=2, max_length=8)


class RegenerateSellerRecipeRequest(BaseModel):
    previous_generation_id: str
    instructions: str = Field(min_length=3, max_length=1000)


class SellerRecipeGenerationResult(BaseModel):
    generation_id: str
    recipe: GeneratedRecipeDraft


class CompatibilityResource(BaseModel):
    resource_type: ResourceType
    resource_id: str


class CompatibilityCheckRequest(CompatibilityResource):
    pass


class CompatibilityBatchRequest(BaseModel):
    items: list[CompatibilityResource] = Field(min_length=1, max_length=100)


class CompatibilityConflict(BaseModel):
    type: str
    allergen: str | None = None
    ingredient: str | None = None
    dietary_preference: str | None = None
    severity: str


class CompatibilityResult(BaseModel):
    resource_type: ResourceType
    resource_id: str
    status: CompatibilityStatus
    conflicts: list[CompatibilityConflict] = Field(default_factory=list)
    unknown_ingredients: list[str] = Field(default_factory=list)


class CompatibilityBatchResult(BaseModel):
    items: list[CompatibilityResult]


class RecommendationEventRequest(BaseModel):
    recommendation_id: str
    item_type: str
    item_id: str
    event: RecommendationEventType


class ProfileInvalidateRequest(BaseModel):
    profile_version: int | None = Field(default=None, ge=1)


class HealthResult(BaseModel):
    status: str
    checks: dict[str, Any] = Field(default_factory=dict)
