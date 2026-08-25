from app.services.nutrition import NutritionCalculator
from tests.support.fixtures import meal_plan,recipe

def test_average_daily_nutrition_scales_servings():
    plan=meal_plan(); facts=NutritionCalculator().average_daily(plan,{'r1':recipe('r1')})
    assert facts.calories==1600  # 400 per serving * 4 servings
    assert facts.protein_g==120
