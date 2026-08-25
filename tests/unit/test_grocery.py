import pytest
from app.services.grocery import UnitNormalizer
from tests.support.fixtures import USER_ID


def test_unit_normalizer_converts_kg_to_g():
    qty,unit=UnitNormalizer().normalize(1.5,'kg')
    assert qty==1500 and unit=='g'

@pytest.mark.asyncio
async def test_meal_plan_grocery_scales_servings(container):
    result=await container.grocery_service.from_meal_plan(USER_ID,'mp1')
    rice=next(x for x in result.items if x.ingredient_id=='rice')
    # recipe serves 2, plan serves 4 => 200g * 2
    assert rice.quantity==400
