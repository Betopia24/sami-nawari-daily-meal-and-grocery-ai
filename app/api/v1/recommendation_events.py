from fastapi import APIRouter,Depends,Response,status
from app.api.deps import get_container,get_user_id
from app.domain.schemas import RecommendationEventRequest

router=APIRouter(prefix='/recommendation-events',tags=['recommendation-events'])

@router.post('',status_code=status.HTTP_204_NO_CONTENT)
async def record(payload:RecommendationEventRequest,user_id=Depends(get_user_id),container=Depends(get_container)):
    await container.event_service.record(user_id,payload)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
