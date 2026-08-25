from datetime import date
from uuid import UUID, uuid4
from app.core.errors import NoCompatibleResults, OutputValidationFailed, ResourceNotFound
from app.domain.enums import ResourceType, GenerationFeature
from app.domain.schemas import MealPlanGenerateResult, ReplacementOptionsResult, ReplacementOption


class MealPlanValidator:
    def validate(self, plan, *, candidates_by_id: dict, requested_days: int, meals_per_day: list[str], profile, compatibility) -> None:
        if len(plan.days) != requested_days:
            raise OutputValidationFailed('Generated meal plan has incorrect number of days')
        for day in plan.days:
            types=[m.meal_type for m in day.meals]
            if set(types) != set(meals_per_day):
                raise OutputValidationFailed('Generated meal plan has incorrect meal types')
            for meal in day.meals:
                recipe=candidates_by_id.get(meal.recipe_id)
                if not recipe:
                    raise OutputValidationFailed(f'Unknown generated recipe_id: {meal.recipe_id}')
                check=compatibility.check(profile,ResourceType.RECIPE,recipe.recipe_id,recipe.ingredients,recipe.dietary_tags)
                if check.status.value != 'safe':
                    raise OutputValidationFailed(f'Generated incompatible recipe: {recipe.recipe_id}')


class MealPlanningService:
    PROMPT_VERSION='meal-plan-v1'
    def __init__(self, profile_service, main_backend, compatibility, llm, generations, validator, candidate_limit: int=200) -> None:
        self._profiles=profile_service; self._main=main_backend; self._compat=compatibility; self._llm=llm; self._generations=generations; self._validator=validator; self._candidate_limit=candidate_limit

    async def generate(self, user_id: UUID, request) -> MealPlanGenerateResult:
        profile=await self._profiles.get(user_id)
        candidates=await self._main.list_recipe_candidates(user_id,self._candidate_limit,None)
        safe=[]
        for r in candidates:
            if r.recipe_id in request.excluded_recipe_ids: continue
            if self._compat.check(profile,ResourceType.RECIPE,r.recipe_id,r.ingredients,r.dietary_tags).status.value=='safe': safe.append(r)
        if not safe: raise NoCompatibleResults('No compatible recipes available for meal planning')
        generation_id=f'gen_mp_{uuid4().hex}'
        await self._generations.create(generation_id=generation_id,user_id=user_id,feature=GenerationFeature.MEAL_PLAN,model=self._llm.model_name,prompt_version=self.PROMPT_VERSION,status='running',metadata={'days':request.days})
        plan=await self._llm.generate_meal_plan(profile=profile,candidates=safe,start_date=request.start_date,days=request.days,meals_per_day=request.meals_per_day,goal=request.goal_override or profile.nutrition_goal)
        self._validator.validate(plan,candidates_by_id={r.recipe_id:r for r in safe},requested_days=request.days,meals_per_day=request.meals_per_day,profile=profile,compatibility=self._compat)
        await self._generations.save_output(generation_id,plan.model_dump(mode='json'))
        return MealPlanGenerateResult(generation_id=generation_id,profile_version=profile.profile_version,plan=plan)

    async def replacement_options(self, user_id: UUID, plan_id: str, item_id: str, request) -> ReplacementOptionsResult:
        profile=await self._profiles.get(user_id)
        plan=await self._main.get_meal_plan(plan_id,user_id)
        flat=[m for d in plan.days for m in d.meals]
        # Main backend should pass its meal-item identifier. The compact domain model used here
        # uses recipe_id as the item identifier; extend MealPlanItem with item_id when integrating.
        current=next((m for m in flat if m.recipe_id==item_id),None)
        if current is None: raise ResourceNotFound('Meal item not found')
        current_recipe=await self._main.get_recipe(current.recipe_id)
        intent=await self._llm.interpret_replacement(request.preference) if request.preference.strip() else None
        candidates=await self._main.list_recipe_candidates(user_id,self._candidate_limit,current.meal_type)
        options=[]
        terms=set(intent.required_terms if intent else [])
        for recipe in candidates:
            if recipe.recipe_id==current.recipe_id: continue
            comp=self._compat.check(profile,ResourceType.RECIPE,recipe.recipe_id,recipe.ingredients,recipe.dietary_tags)
            if comp.status.value!='safe': continue
            hay=' '.join([recipe.title,recipe.cuisine or '',*recipe.goal_tags,*recipe.dietary_tags]).lower()
            term_score=(sum(1 for t in terms if t in hay)/max(len(terms),1)) if terms else 0.5
            nutrition_delta=abs(recipe.nutrition_per_serving.calories-current_recipe.nutrition_per_serving.calories)
            similarity=max(0.0,1-min(nutrition_delta/800,1))
            score=min(1.0,0.6*similarity+0.4*term_score)
            options.append(ReplacementOption(recipe_id=recipe.recipe_id,compatibility=comp.status,similarity_score=round(score,4),reason='Compatible alternative matched to your request.'))
        options.sort(key=lambda x:x.similarity_score,reverse=True)
        return ReplacementOptionsResult(current_recipe_id=current.recipe_id,options=options[:request.limit])

