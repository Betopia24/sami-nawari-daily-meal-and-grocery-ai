import pytest
from app.domain.models import GeneratedRecipeDraft,GeneratedRecipeIngredient,GeneratedRecipeStep
from app.services.seller_recipe import SellerRecipeValidator
from app.core.errors import OutputValidationFailed
from tests.support.fixtures import seller_food,SELLER_USER_ID

@pytest.mark.asyncio
async def test_seller_recipe_generation_uses_only_seller_ingredients(container):
    result=await container.seller_recipe_service.generate(SELLER_USER_ID,'sf1','en')
    allowed={i.ingredient_id for i in seller_food().ingredients}
    assert {i.ingredient_id for i in result.recipe.ingredients}<=allowed


def test_validator_rejects_invented_required_ingredient():
    food=seller_food(); recipe=GeneratedRecipeDraft(title='X',summary='X',servings=4,prep_time_minutes=1,cook_time_minutes=1,ingredients=[GeneratedRecipeIngredient(ingredient_id='peanut',name='Peanut',quantity=1,unit='g')],steps=[GeneratedRecipeStep(step_number=1,instruction='Cook safely.')])
    with pytest.raises(OutputValidationFailed): SellerRecipeValidator().validate(food,recipe)
