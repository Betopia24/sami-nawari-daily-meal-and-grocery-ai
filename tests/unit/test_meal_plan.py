import pytest
from app.domain.schemas import MealPlanGenerateRequest,ReplacementOptionsRequest
from tests.support.fixtures import USER_ID

@pytest.mark.asyncio
async def test_generate_meal_plan_is_structured_and_valid(container):
    req=MealPlanGenerateRequest(start_date='2026-08-26',days=2,meals_per_day=['lunch'])
    result=await container.meal_planning_service.generate(USER_ID,req)
    assert len(result.plan.days)==2
    assert all(d.meals[0].recipe_id!='bad' for d in result.plan.days)

@pytest.mark.asyncio
async def test_replacement_excludes_current_and_conflicts(container):
    result=await container.meal_planning_service.replacement_options(USER_ID,'mp1','r1',ReplacementOptionsRequest(preference='fish',limit=5))
    ids=[x.recipe_id for x in result.options]
    assert 'r1' not in ids and 'bad' not in ids and 'r2' in ids
