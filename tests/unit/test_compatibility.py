from app.services.compatibility import CompatibilityEngine
from app.domain.enums import ResourceType,CompatibilityStatus
from tests.support.fixtures import profile,ingredients_safe,ingredients_peanut

def test_safe_ingredients_are_safe():
    result=CompatibilityEngine().check(profile(),ResourceType.FOOD,'f1',ingredients_safe(),{'halal'})
    assert result.status is CompatibilityStatus.SAFE

def test_peanut_conflict_is_detected():
    result=CompatibilityEngine().check(profile(),ResourceType.FOOD,'f1',ingredients_peanut(),set())
    assert result.status is CompatibilityStatus.CONFLICT
    assert result.conflicts[0].allergen=='peanut'
