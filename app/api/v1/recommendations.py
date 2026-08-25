from fastapi import APIRouter, Depends
from app.api.deps import get_container, get_user_id, get_request_id
from app.domain.schemas import APIResponse, FoodRecommendationRequest, RecipeRecommendationRequest, RecommendationResult

router=APIRouter(prefix='/recommendations',tags=['recommendations'])

@router.post('/foods',response_model=APIResponse[RecommendationResult])
async def recommend_foods(payload:FoodRecommendationRequest,user_id=Depends(get_user_id),container=Depends(get_container),request_id=Depends(get_request_id)):
    data=await container.recommendation_service.foods(user_id,payload)
    return APIResponse(request_id=request_id,data=data)

@router.post('/recipes',response_model=APIResponse[RecommendationResult])
async def recommend_recipes(payload:RecipeRecommendationRequest,user_id=Depends(get_user_id),container=Depends(get_container),request_id=Depends(get_request_id)):
    data=await container.recommendation_service.recipes(user_id,payload)
    return APIResponse(request_id=request_id,data=data)
