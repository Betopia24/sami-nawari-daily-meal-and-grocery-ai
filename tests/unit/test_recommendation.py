import pytest
from app.domain.schemas import FoodRecommendationRequest,RecipeRecommendationRequest
from tests.support.fixtures import USER_ID

@pytest.mark.asyncio
async def test_food_recommendation_filters_allergy_conflict(container):
    result=await container.recommendation_service.foods(USER_ID,FoodRecommendationRequest(limit=10,meal_type='lunch'))
    ids=[x.item_id for x in result.items]
    assert 'bad' not in ids and 'f1' in ids
    assert ids[0]=='f1'

@pytest.mark.asyncio
async def test_recipe_recommendation_filters_conflict(container):
    result=await container.recommendation_service.recipes(USER_ID,RecipeRecommendationRequest(limit=10))
    assert 'bad' not in [x.item_id for x in result.items]
