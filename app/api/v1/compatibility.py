from fastapi import APIRouter,Depends
from app.api.deps import get_container,get_user_id,get_request_id
from app.domain.schemas import APIResponse,CompatibilityCheckRequest,CompatibilityBatchRequest,CompatibilityResult,CompatibilityBatchResult

router=APIRouter(prefix='/compatibility',tags=['compatibility'])

@router.post('/check',response_model=APIResponse[CompatibilityResult])
async def check(payload:CompatibilityCheckRequest,user_id=Depends(get_user_id),container=Depends(get_container),request_id=Depends(get_request_id)):
    data=await container.compatibility_service.check(user_id,payload.resource_type,payload.resource_id)
    return APIResponse(request_id=request_id,data=data)

@router.post('/check-batch',response_model=APIResponse[CompatibilityBatchResult])
async def check_batch(payload:CompatibilityBatchRequest,user_id=Depends(get_user_id),container=Depends(get_container),request_id=Depends(get_request_id)):
    data=await container.compatibility_service.batch(user_id,payload.items)
    return APIResponse(request_id=request_id,data=data)
