from uuid import UUID, uuid4
from app.core.errors import OutputValidationFailed, ResourceNotFound
from app.domain.enums import GenerationFeature
from app.domain.models import GeneratedRecipeDraft
from app.domain.schemas import SellerRecipeGenerationResult


class SellerRecipeValidator:
    def validate(self, food, recipe: GeneratedRecipeDraft) -> None:
        allowed={i.ingredient_id for i in food.ingredients}
        generated={i.ingredient_id for i in recipe.ingredients}
        illegal=generated-allowed
        if illegal:
            raise OutputValidationFailed(f'Generated recipe introduced unapproved ingredient IDs: {sorted(illegal)}')
        if not recipe.steps:
            raise OutputValidationFailed('Generated recipe has no preparation steps')


class SellerRecipeService:
    PROMPT_VERSION='seller-recipe-v1'
    def __init__(self, main_backend, llm, generations, validator) -> None:
        self._main=main_backend; self._llm=llm; self._generations=generations; self._validator=validator

    async def generate(self,user_id:UUID,food_id:str,language:str) -> SellerRecipeGenerationResult:
        food=await self._main.get_seller_food_draft(food_id,user_id)
        generation_id=f'gen_recipe_{uuid4().hex}'
        await self._generations.create(generation_id=generation_id,user_id=user_id,feature=GenerationFeature.SELLER_RECIPE,model=self._llm.model_name,prompt_version=self.PROMPT_VERSION,status='running',metadata={'food_id':food_id})
        recipe=await self._llm.generate_seller_recipe(food=food,language=language)
        self._validator.validate(food,recipe)
        await self._generations.save_output(generation_id,recipe.model_dump(mode='json'))
        return SellerRecipeGenerationResult(generation_id=generation_id,recipe=recipe)

    async def regenerate(self,user_id:UUID,food_id:str,previous_generation_id:str,instructions:str) -> SellerRecipeGenerationResult:
        food=await self._main.get_seller_food_draft(food_id,user_id)
        previous_data=await self._generations.get_output(previous_generation_id)
        if not previous_data: raise ResourceNotFound('Previous generated recipe not found')
        previous=GeneratedRecipeDraft.model_validate(previous_data)
        generation_id=f'gen_recipe_{uuid4().hex}'
        await self._generations.create(generation_id=generation_id,user_id=user_id,feature=GenerationFeature.SELLER_RECIPE_REGENERATION,model=self._llm.model_name,prompt_version=self.PROMPT_VERSION,status='running',metadata={'food_id':food_id,'previous_generation_id':previous_generation_id})
        recipe=await self._llm.regenerate_seller_recipe(food=food,previous=previous,instructions=instructions)
        self._validator.validate(food,recipe)
        await self._generations.save_output(generation_id,recipe.model_dump(mode='json'))
        return SellerRecipeGenerationResult(generation_id=generation_id,recipe=recipe)
