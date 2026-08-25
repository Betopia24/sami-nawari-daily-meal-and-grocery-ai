from datetime import date
from uuid import UUID
from app.domain.models import *

USER_ID=UUID('11111111-1111-1111-1111-111111111111')
SELLER_USER_ID=UUID('22222222-2222-2222-2222-222222222222')


def ingredients_safe():
    return [IngredientAmount(ingredient_id='rice',name='Rice',quantity=200,unit='g',category='grains'),IngredientAmount(ingredient_id='chicken',name='Chicken',quantity=150,unit='g',category='protein')]

def ingredients_peanut():
    return [IngredientAmount(ingredient_id='peanut_oil',name='Peanut Oil',quantity=10,unit='ml',category='other',allergens={'peanut'})]

def profile():
    return UserAIProfile(user_id=USER_ID,profile_version=3,dietary_preferences={'halal'},allergies={'peanut'},preferred_cuisines={'bangladeshi'},nutrition_goal='healthy',household_size=4,language='en')

def recipe(rid='r1',title='Chicken Rice',ingredients=None,calories=400,cuisine='bangladeshi',meal_types=None):
    return Recipe(recipe_id=rid,title=title,cuisine=cuisine,meal_types=set(meal_types or {'lunch','dinner'}),dietary_tags={'halal'},goal_tags={'healthy'},ingredients=ingredients or ingredients_safe(),servings=2,rating=4.7,popularity_score=.8,nutrition_per_serving=NutritionFacts(calories=calories,protein_g=30,carbs_g=50,fat_g=10,fiber_g=5))

def food(fid='f1',ingredients=None,rating=4.8):
    return FoodItem(food_id=fid,seller_id='s1',name='Homemade Chicken Rice',cuisine='bangladeshi',meal_types={'lunch'},dietary_tags={'halal'},goal_tags={'healthy'},ingredients=ingredients or ingredients_safe(),rating=rating,popularity_score=.7,distance_km=2)

def meal_plan():
    return StoredMealPlan(plan_id='mp1',user_id=USER_ID,version=1,days=[MealPlanDay(date=date(2026,8,26),meals=[MealPlanItem(meal_type='lunch',recipe_id='r1',servings=4)])])

def seller_food():
    return SellerFoodDraft(food_id='sf1',seller_user_id=SELLER_USER_ID,seller_id='seller1',name='Chicken Khichuri',cuisine='bangladeshi',servings=4,prep_time_minutes=20,cook_time_minutes=40,preparation_notes='Wash ingredients and prepare spices.',cooking_method='Cook together until tender.',ingredients=ingredients_safe(),details='Traditional homemade meal')
