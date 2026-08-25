from app.domain.enums import CompatibilityStatus, ResourceType
from app.domain.models import UserAIProfile, FoodItem, Recipe
from app.domain.schemas import CompatibilityResult, CompatibilityConflict


class CompatibilityEngine:
    DIET_CONFLICT_FLAGS = {
        'vegan': {'contains_meat','contains_fish','contains_dairy','contains_egg','non_vegan'},
        'vegetarian': {'contains_meat','contains_fish','non_vegetarian'},
        'halal': {'non_halal','contains_pork','contains_alcohol'},
    }

    def check(self, profile: UserAIProfile, resource_type: ResourceType, resource_id: str, ingredients, dietary_tags: set[str]) -> CompatibilityResult:
        conflicts=[]; unknown=[]
        for ingredient in ingredients:
            if not ingredient.verified:
                unknown.append(ingredient.name)
            overlap={x.lower() for x in ingredient.allergens} & {x.lower() for x in profile.allergies}
            for allergen in sorted(overlap):
                conflicts.append(CompatibilityConflict(type='allergy',allergen=allergen,ingredient=ingredient.name,severity='conflict'))

        all_flags={flag.lower() for ing in ingredients for flag in ing.flags}
        for pref in {x.lower() for x in profile.dietary_preferences}:
            bad=self.DIET_CONFLICT_FLAGS.get(pref,set())
            if all_flags & bad:
                conflicts.append(CompatibilityConflict(type='dietary',dietary_preference=pref,severity='conflict'))

        if conflicts: status=CompatibilityStatus.CONFLICT
        elif unknown: status=CompatibilityStatus.UNKNOWN
        else: status=CompatibilityStatus.SAFE
        return CompatibilityResult(resource_type=resource_type,resource_id=resource_id,status=status,conflicts=conflicts,unknown_ingredients=unknown)

    def is_safe(self, profile: UserAIProfile, resource: FoodItem | Recipe, resource_type: ResourceType) -> bool:
        resource_id=resource.food_id if isinstance(resource,FoodItem) else resource.recipe_id
        return self.check(profile,resource_type,resource_id,resource.ingredients,resource.dietary_tags).status == CompatibilityStatus.SAFE
