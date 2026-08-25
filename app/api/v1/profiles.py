from uuid import UUID
from fastapi import APIRouter,Depends
from app.api.deps import get_container,require_service_auth,get_request_id
from app.domain.schemas import APIResponse,ProfileInvalidateRequest

router=APIRouter(prefix='/users',tags=['profile-cache'])

@router.post('/{user_id}/profile-cache/invalidate',response_model=APIResponse[dict])
async def invalidate(user_id:UUID,payload:ProfileInvalidateRequest,_=Depends(require_service_auth),container=Depends(get_container),request_id=Depends(get_request_id)):
    await container.profile_service.invalidate(user_id)
    return APIResponse(request_id=request_id,data={'invalidated':True,'profile_version':payload.profile_version})
