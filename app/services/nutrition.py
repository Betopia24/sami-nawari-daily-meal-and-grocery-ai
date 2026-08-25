from uuid import UUID, uuid4
from app.domain.enums import GenerationFeature
from app.domain.models import NutritionFacts
from app.domain.schemas import NutritionInsightResult
from app.core.errors import ResourceNotFound


class NutritionCalculator:
    def average_daily(self, plan, recipes_by_id: dict) -> NutritionFacts:
        if not plan.days: return NutritionFacts()
        total=NutritionFacts()
        for day in plan.days:
            day_total=NutritionFacts()
            for meal in day.meals:
                recipe=recipes_by_id[meal.recipe_id]
                day_total=day_total.add(recipe.nutrition_per_serving.scaled(meal.servings))
            total=total.add(day_total)
        return total.scaled(1/len(plan.days))


class NutritionInsightService:
    PROMPT_VERSION='nutrition-insight-v1'
    def __init__(self, profile_service, main_backend, llm, generations, calculator) -> None:
        self._profiles=profile_service; self._main=main_backend; self._llm=llm; self._generations=generations; self._calculator=calculator

    async def generate(self,user_id:UUID,plan_id:str) -> NutritionInsightResult:
        profile=await self._profiles.get(user_id)
        plan=await self._main.get_meal_plan(plan_id,user_id)
        ids={m.recipe_id for d in plan.days for m in d.meals}
        recipes={rid:await self._main.get_recipe(rid) for rid in ids}
        nutrition=self._calculator.average_daily(plan,recipes)
        generation_id=f'gen_insight_{uuid4().hex}'
        await self._generations.create(generation_id=generation_id,user_id=user_id,feature=GenerationFeature.NUTRITION_INSIGHT,model=self._llm.model_name,prompt_version=self.PROMPT_VERSION,status='running',metadata={'plan_id':plan_id,'plan_version':plan.version})
        insight=await self._llm.generate_nutrition_insight(profile=profile,nutrition=nutrition)
        output={'nutrition':nutrition.model_dump(),'insight':insight.model_dump()}
        await self._generations.save_output(generation_id,output)
        return NutritionInsightResult(generation_id=generation_id,nutrition=nutrition,insight=insight)


    async def latest(self, user_id: UUID, plan_id: str) -> NutritionInsightResult:
        found=await self._generations.get_latest_output(user_id=user_id,feature=GenerationFeature.NUTRITION_INSIGHT,metadata_match={'plan_id':plan_id})
        if not found:
            raise ResourceNotFound('No nutrition insight generated for this meal plan')
        generation_id,output=found
        return NutritionInsightResult(generation_id=generation_id,**output)
