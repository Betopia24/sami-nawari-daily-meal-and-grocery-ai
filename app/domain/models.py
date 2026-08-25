from __future__ import annotations
from datetime import date
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class NutritionFacts(BaseModel):
    calories: float = 0
    protein_g: float = 0
    carbs_g: float = 0
    fat_g: float = 0
    fiber_g: float = 0
    sugar_g: float = 0
    sodium_mg: float = 0

    def scaled(self, factor: float) -> 'NutritionFacts':
        return NutritionFacts(**{k: getattr(self, k) * factor for k in NutritionFacts.model_fields})

    def add(self, other: 'NutritionFacts') -> 'NutritionFacts':
        return NutritionFacts(**{k: getattr(self, k) + getattr(other, k) for k in NutritionFacts.model_fields})


class IngredientAmount(BaseModel):
    ingredient_id: str
    name: str
    quantity: float = Field(gt=0)
    unit: str
    category: str = 'other'
    allergens: set[str] = Field(default_factory=set)
    flags: set[str] = Field(default_factory=set)
    verified: bool = True


class UserAIProfile(BaseModel):
    user_id: UUID
    profile_version: int = 1
    dietary_preferences: set[str] = Field(default_factory=set)
    allergies: set[str] = Field(default_factory=set)
    preferred_cuisines: set[str] = Field(default_factory=set)
    nutrition_goal: str | None = None
    household_size: int = Field(default=1, ge=1, le=20)
    cooking_frequency: str | None = None
    language: str = 'en'
    favorite_seller_ids: set[str] = Field(default_factory=set)
    behavior_affinity: dict[str, float] = Field(default_factory=dict)


class FoodItem(BaseModel):
    food_id: str
    seller_id: str
    name: str
    cuisine: str | None = None
    meal_types: set[str] = Field(default_factory=set)
    dietary_tags: set[str] = Field(default_factory=set)
    goal_tags: set[str] = Field(default_factory=set)
    ingredients: list[IngredientAmount] = Field(default_factory=list)
    rating: float = Field(default=0, ge=0, le=5)
    popularity_score: float = Field(default=0, ge=0, le=1)
    distance_km: float | None = Field(default=None, ge=0)
    available: bool = True


class Recipe(BaseModel):
    recipe_id: str
    title: str
    cuisine: str | None = None
    meal_types: set[str] = Field(default_factory=set)
    dietary_tags: set[str] = Field(default_factory=set)
    goal_tags: set[str] = Field(default_factory=set)
    ingredients: list[IngredientAmount] = Field(default_factory=list)
    servings: int = Field(default=1, ge=1)
    prep_time_minutes: int = Field(default=0, ge=0)
    cook_time_minutes: int = Field(default=0, ge=0)
    rating: float = Field(default=0, ge=0, le=5)
    popularity_score: float = Field(default=0, ge=0, le=1)
    nutrition_per_serving: NutritionFacts = Field(default_factory=NutritionFacts)
    seller_id: str | None = None


class MealPlanItem(BaseModel):
    meal_type: str
    recipe_id: str
    servings: int = Field(ge=1)


class MealPlanDay(BaseModel):
    date: date
    meals: list[MealPlanItem]


class MealPlanDraft(BaseModel):
    days: list[MealPlanDay]


class StoredMealPlan(BaseModel):
    plan_id: str
    user_id: UUID
    version: int = 1
    days: list[MealPlanDay]


class GeneratedRecipeIngredient(BaseModel):
    ingredient_id: str
    name: str
    quantity: float = Field(gt=0)
    unit: str


class GeneratedRecipeStep(BaseModel):
    step_number: int = Field(ge=1)
    instruction: str = Field(min_length=3)


class GeneratedRecipeDraft(BaseModel):
    title: str
    summary: str
    servings: int = Field(ge=1)
    prep_time_minutes: int = Field(ge=0)
    cook_time_minutes: int = Field(ge=0)
    ingredients: list[GeneratedRecipeIngredient]
    steps: list[GeneratedRecipeStep]
    suggested_missing_ingredients: list[str] = Field(default_factory=list)


class SellerFoodDraft(BaseModel):
    food_id: str
    seller_user_id: UUID
    seller_id: str
    name: str
    cuisine: str | None = None
    servings: int = Field(default=1, ge=1)
    prep_time_minutes: int = Field(default=0, ge=0)
    cook_time_minutes: int = Field(default=0, ge=0)
    preparation_notes: str | None = None
    cooking_method: str | None = None
    ingredients: list[IngredientAmount]
    details: str | None = None


class NutritionInsight(BaseModel):
    summary: str
    positive_points: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class ReplacementIntent(BaseModel):
    required_terms: list[str] = Field(default_factory=list)
    excluded_terms: list[str] = Field(default_factory=list)
    prefer_lighter: bool = False
    prefer_cheaper: bool = False
