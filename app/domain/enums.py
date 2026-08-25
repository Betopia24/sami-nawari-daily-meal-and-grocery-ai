from enum import StrEnum


class CompatibilityStatus(StrEnum):
    SAFE = 'safe'
    CONFLICT = 'conflict'
    POTENTIAL_CONFLICT = 'potential_conflict'
    UNKNOWN = 'unknown'


class ResourceType(StrEnum):
    FOOD = 'food'
    RECIPE = 'recipe'


class RecommendationItemType(StrEnum):
    FOOD = 'food'
    RECIPE = 'recipe'


class RecommendationEventType(StrEnum):
    IMPRESSION = 'impression'
    CLICKED = 'clicked'
    SAVED = 'saved'
    ORDERED = 'ordered'
    DISMISSED = 'dismissed'


class GenerationFeature(StrEnum):
    MEAL_PLAN = 'meal_plan'
    NUTRITION_INSIGHT = 'nutrition_insight'
    SELLER_RECIPE = 'seller_recipe'
    SELLER_RECIPE_REGENERATION = 'seller_recipe_regeneration'
