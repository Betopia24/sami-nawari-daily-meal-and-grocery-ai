from fastapi import APIRouter,Depends
from app.api.deps import get_container,get_user_id,get_request_id
from app.domain.schemas import APIResponse,GroceryFromMealPlanRequest,GroceryFromRecipeRequest,GroceryDraftResult

router=APIRouter(prefix='/grocery-drafts',tags=['grocery'])

@router.post('/from-meal-plan',response_model=APIResponse[GroceryDraftResult])
async def from_meal_plan(payload:GroceryFromMealPlanRequest,user_id=Depends(get_user_id),container=Depends(get_container),request_id=Depends(get_request_id)):
    data=await container.grocery_service.from_meal_plan(user_id,payload.meal_plan_id)
    return APIResponse(request_id=request_id,data=data)

@router.post('/from-recipe',response_model=APIResponse[GroceryDraftResult])
async def from_recipe(payload:GroceryFromRecipeRequest,user_id=Depends(get_user_id),container=Depends(get_container),request_id=Depends(get_request_id)):
    data=await container.grocery_service.from_recipe(user_id,payload.recipe_id,payload.servings)
    return APIResponse(request_id=request_id,data=data)
