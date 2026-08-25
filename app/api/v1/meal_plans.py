from fastapi import APIRouter, Depends, Header
from app.api.deps import get_container,get_user_id,get_request_id
from app.domain.schemas import APIResponse,Meta,MealPlanGenerateRequest,MealPlanGenerateResult,ReplacementOptionsRequest,ReplacementOptionsResult,NutritionInsightResult

router=APIRouter(prefix='/meal-plans',tags=['meal-plans'])

@router.post('/generate',response_model=APIResponse[MealPlanGenerateResult])
async def generate_meal_plan(payload:MealPlanGenerateRequest,user_id=Depends(get_user_id),container=Depends(get_container),request_id=Depends(get_request_id),idempotency_key:str|None=Header(default=None,alias='Idempotency-Key')):
    async def factory():
        await container.rate_limiter.check(user_id=str(user_id),feature='meal-plan')
        result=await container.meal_planning_service.generate(user_id,payload)
        return result.model_dump(mode='json')
    raw,cached=await container.idempotency.execute(scope='meal-plan',user_id=str(user_id),key=idempotency_key,factory=factory)
    return APIResponse(request_id=request_id,data=MealPlanGenerateResult.model_validate(raw),meta=Meta(cached=cached))

@router.post('/{plan_id}/items/{item_id}/replacement-options',response_model=APIResponse[ReplacementOptionsResult])
async def replacement_options(plan_id:str,item_id:str,payload:ReplacementOptionsRequest,user_id=Depends(get_user_id),container=Depends(get_container),request_id=Depends(get_request_id)):
    await container.rate_limiter.check(user_id=str(user_id),feature='meal-replacement')
    data=await container.meal_planning_service.replacement_options(user_id,plan_id,item_id,payload)
    return APIResponse(request_id=request_id,data=data)

@router.post('/{plan_id}/insights',response_model=APIResponse[NutritionInsightResult])
async def nutrition_insight(plan_id:str,user_id=Depends(get_user_id),container=Depends(get_container),request_id=Depends(get_request_id),idempotency_key:str|None=Header(default=None,alias='Idempotency-Key')):
    async def factory():
        await container.rate_limiter.check(user_id=str(user_id),feature='nutrition-insight')
        result=await container.nutrition_service.generate(user_id,plan_id)
        return result.model_dump(mode='json')
    raw,cached=await container.idempotency.execute(scope=f'nutrition:{plan_id}',user_id=str(user_id),key=idempotency_key,factory=factory)
    return APIResponse(request_id=request_id,data=NutritionInsightResult.model_validate(raw),meta=Meta(cached=cached))


@router.get('/{plan_id}/insights/latest',response_model=APIResponse[NutritionInsightResult])
async def latest_nutrition_insight(plan_id:str,user_id=Depends(get_user_id),container=Depends(get_container),request_id=Depends(get_request_id)):
    data=await container.nutrition_service.latest(user_id,plan_id)
    return APIResponse(request_id=request_id,data=data,meta=Meta(cached=True))
