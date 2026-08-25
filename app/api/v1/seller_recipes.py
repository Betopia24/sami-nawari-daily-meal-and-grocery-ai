from fastapi import APIRouter,Depends,Header
from app.api.deps import get_container,get_user_id,get_request_id
from app.domain.schemas import APIResponse,Meta,GenerateSellerRecipeRequest,RegenerateSellerRecipeRequest,SellerRecipeGenerationResult

router=APIRouter(prefix='/seller-foods',tags=['seller-recipe-ai'])

@router.post('/{food_id}/recipe-drafts/generate',response_model=APIResponse[SellerRecipeGenerationResult])
async def generate(food_id:str,payload:GenerateSellerRecipeRequest,user_id=Depends(get_user_id),container=Depends(get_container),request_id=Depends(get_request_id),idempotency_key:str|None=Header(default=None,alias='Idempotency-Key')):
    async def factory():
        await container.rate_limiter.check(user_id=str(user_id),feature='seller-recipe')
        result=await container.seller_recipe_service.generate(user_id,food_id,payload.language)
        return result.model_dump(mode='json')
    raw,cached=await container.idempotency.execute(scope=f'seller-recipe:{food_id}',user_id=str(user_id),key=idempotency_key,factory=factory)
    return APIResponse(request_id=request_id,data=SellerRecipeGenerationResult.model_validate(raw),meta=Meta(cached=cached))

@router.post('/{food_id}/recipe-drafts/regenerate',response_model=APIResponse[SellerRecipeGenerationResult])
async def regenerate(food_id:str,payload:RegenerateSellerRecipeRequest,user_id=Depends(get_user_id),container=Depends(get_container),request_id=Depends(get_request_id),idempotency_key:str|None=Header(default=None,alias='Idempotency-Key')):
    async def factory():
        await container.rate_limiter.check(user_id=str(user_id),feature='seller-recipe-regen')
        result=await container.seller_recipe_service.regenerate(user_id,food_id,payload.previous_generation_id,payload.instructions)
        return result.model_dump(mode='json')
    raw,cached=await container.idempotency.execute(scope=f'seller-recipe-regen:{food_id}',user_id=str(user_id),key=idempotency_key,factory=factory)
    return APIResponse(request_id=request_id,data=SellerRecipeGenerationResult.model_validate(raw),meta=Meta(cached=cached))
