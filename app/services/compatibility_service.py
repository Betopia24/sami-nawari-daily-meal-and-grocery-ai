from uuid import UUID
from app.domain.enums import ResourceType
from app.domain.schemas import CompatibilityBatchResult


class CompatibilityService:
    def __init__(self,profile_service,main_backend,engine) -> None:
        self._profiles=profile_service; self._main=main_backend; self._engine=engine

    async def check(self,user_id:UUID,resource_type:ResourceType,resource_id:str):
        profile=await self._profiles.get(user_id)
        if resource_type==ResourceType.FOOD:
            resource=await self._main.get_food(resource_id); ingredients=resource.ingredients; tags=resource.dietary_tags
        else:
            resource=await self._main.get_recipe(resource_id); ingredients=resource.ingredients; tags=resource.dietary_tags
        return self._engine.check(profile,resource_type,resource_id,ingredients,tags)

    async def batch(self,user_id:UUID,items):
        results=[]
        for item in items:
            results.append(await self.check(user_id,item.resource_type,item.resource_id))
        return CompatibilityBatchResult(items=results)
