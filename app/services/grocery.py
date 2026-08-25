from collections import defaultdict
from uuid import UUID
from app.domain.schemas import GroceryDraftResult, GroceryItem


class UnitNormalizer:
    FACTORS={
        'g':('g',1.0),'gram':('g',1.0),'grams':('g',1.0),'kg':('g',1000.0),'kilogram':('g',1000.0),
        'ml':('ml',1.0),'milliliter':('ml',1.0),'l':('ml',1000.0),'liter':('ml',1000.0),'litre':('ml',1000.0),
        'pc':('pc',1.0),'pcs':('pc',1.0),'piece':('pc',1.0),'pieces':('pc',1.0),
    }
    def normalize(self, quantity: float, unit: str) -> tuple[float,str]:
        canonical,factor=self.FACTORS.get(unit.strip().lower(),(unit.strip().lower(),1.0))
        return quantity*factor,canonical


class GroceryGeneratorService:
    def __init__(self, profile_service, main_backend, unit_normalizer) -> None:
        self._profiles=profile_service; self._main=main_backend; self._units=unit_normalizer

    async def from_meal_plan(self,user_id:UUID,plan_id:str) -> GroceryDraftResult:
        profile=await self._profiles.get(user_id)
        plan=await self._main.get_meal_plan(plan_id,user_id)
        totals={}
        for day in plan.days:
            for meal in day.meals:
                recipe=await self._main.get_recipe(meal.recipe_id)
                scale=meal.servings/recipe.servings
                self._merge_recipe(totals,recipe,scale)
        return GroceryDraftResult(source_type='meal_plan',source_id=plan_id,items=self._to_items(totals))

    async def from_recipe(self,user_id:UUID,recipe_id:str,servings:int) -> GroceryDraftResult:
        await self._profiles.get(user_id)  # validates user/profile and keeps endpoint personalization contract
        recipe=await self._main.get_recipe(recipe_id)
        totals={}; self._merge_recipe(totals,recipe,servings/recipe.servings)
        return GroceryDraftResult(source_type='recipe',source_id=recipe_id,items=self._to_items(totals))

    def _merge_recipe(self,totals,recipe,scale:float):
        for ing in recipe.ingredients:
            qty,unit=self._units.normalize(ing.quantity*scale,ing.unit)
            key=(ing.ingredient_id,unit)
            if key not in totals: totals[key]={'name':ing.name,'quantity':0.0,'category':ing.category}
            totals[key]['quantity']+=qty

    def _to_items(self,totals):
        result=[]
        for (ingredient_id,unit),data in sorted(totals.items(),key=lambda x:(x[1]['category'],x[1]['name'])):
            result.append(GroceryItem(ingredient_id=ingredient_id,name=data['name'],quantity=round(data['quantity'],3),unit=unit,category=data['category']))
        return result
