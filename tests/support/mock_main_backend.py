from fastapi import FastAPI,Header,HTTPException
from tests.support.fixtures import USER_ID,SELLER_USER_ID,profile,food,recipe,meal_plan,seller_food
app=FastAPI()

def data(x): return {'data':x.model_dump(mode='json') if hasattr(x,'model_dump') else x}
@app.get('/internal/ai/users/{user_id}/profile')
async def p(user_id:str):
    if user_id==str(USER_ID): return data(profile())
    if user_id==str(SELLER_USER_ID): return data(profile().model_copy(update={'user_id':SELLER_USER_ID}))
    raise HTTPException(404)
@app.get('/internal/ai/foods/candidates')
async def foods(user_id:str,limit:int=200,meal_type:str|None=None): return {'data':[food('f1').model_dump(mode='json')]}
@app.get('/internal/ai/recipes/candidates')
async def recipes(user_id:str,limit:int=200,meal_type:str|None=None): return {'data':[recipe('r1').model_dump(mode='json'),recipe('r2','Fish Rice').model_dump(mode='json')]}
@app.get('/internal/ai/foods/{food_id}')
async def one_food(food_id:str): return data(food(food_id))
@app.get('/internal/ai/recipes/{recipe_id}')
async def one_recipe(recipe_id:str): return data(recipe(recipe_id))
@app.get('/internal/ai/meal-plans/{plan_id}')
async def plan(plan_id:str,user_id:str): return data(meal_plan())
@app.get('/internal/ai/seller-foods/{food_id}/draft')
async def sf(food_id:str,seller_user_id:str): return data(seller_food())
