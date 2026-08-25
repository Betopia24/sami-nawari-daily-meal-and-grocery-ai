from uuid import UUID


class RecommendationEventService:
    def __init__(self, repository) -> None: self._repo=repository
    async def record(self,user_id:UUID,request) -> None:
        await self._repo.add(user_id=user_id,recommendation_id=request.recommendation_id,item_type=request.item_type,item_id=request.item_id,event=request.event.value)
