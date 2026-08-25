from uuid import UUID
from sqlalchemy import select
from app.domain.enums import GenerationFeature
from app.infrastructure.db.models import AIGenerationRun, RecommendationEvent


class SQLGenerationRepository:
    def __init__(self, session_factory) -> None:
        self._session_factory=session_factory

    async def create(self, *, generation_id: str, user_id: UUID, feature: GenerationFeature, model: str, prompt_version: str, status: str, metadata: dict) -> None:
        async with self._session_factory() as session:
            session.add(AIGenerationRun(
                generation_id=generation_id,user_id=str(user_id),feature=feature.value,model=model,
                prompt_version=prompt_version,status=status,metadata_json=metadata,
            ))
            await session.commit()

    async def get_output(self, generation_id: str) -> dict | None:
        async with self._session_factory() as session:
            row=await session.get(AIGenerationRun,generation_id)
            return row.output_json if row else None

    async def save_output(self, generation_id: str, output: dict, status: str='completed') -> None:
        async with self._session_factory() as session:
            row=await session.get(AIGenerationRun,generation_id)
            if row:
                row.output_json=output; row.status=status
                await session.commit()

    async def get_latest_output(self, *, user_id: UUID, feature: GenerationFeature, metadata_match: dict) -> tuple[str, dict] | None:
        async with self._session_factory() as session:
            result=await session.execute(
                select(AIGenerationRun)
                .where(AIGenerationRun.user_id==str(user_id),AIGenerationRun.feature==feature.value,AIGenerationRun.status=='completed')
                .order_by(AIGenerationRun.created_at.desc())
                .limit(50)
            )
            for row in result.scalars():
                if all(row.metadata_json.get(k)==v for k,v in metadata_match.items()) and row.output_json:
                    return row.generation_id,row.output_json
        return None


class SQLRecommendationEventRepository:
    def __init__(self, session_factory) -> None:
        self._session_factory=session_factory

    async def add(self, *, user_id: UUID, recommendation_id: str, item_type: str, item_id: str, event: str) -> None:
        async with self._session_factory() as session:
            session.add(RecommendationEvent(user_id=str(user_id),recommendation_id=recommendation_id,item_type=item_type,item_id=item_id,event=event))
            await session.commit()


class DBHealthRepository:
    def __init__(self, database) -> None: self._database=database
    async def ping(self) -> bool: return await self._database.ping()


class InMemoryGenerationRepository:
    def __init__(self) -> None: self.rows={}
    async def create(self, **kwargs) -> None: self.rows[kwargs['generation_id']]={**kwargs,'output':None}
    async def get_output(self,generation_id:str):
        row=self.rows.get(generation_id); return row.get('output') if row else None
    async def save_output(self,generation_id:str,output:dict,status:str='completed') -> None:
        if generation_id in self.rows: self.rows[generation_id]['output']=output; self.rows[generation_id]['status']=status
    async def get_latest_output(self, *, user_id: UUID, feature: GenerationFeature, metadata_match: dict):
        rows=[(gid,row) for gid,row in self.rows.items() if row.get('user_id')==user_id and row.get('feature')==feature and row.get('status')=='completed' and all(row.get('metadata',{}).get(k)==v for k,v in metadata_match.items()) and row.get('output')]
        if not rows: return None
        gid,row=rows[-1]; return gid,row['output']


class InMemoryRecommendationEventRepository:
    def __init__(self) -> None: self.events=[]
    async def add(self, **kwargs) -> None: self.events.append(kwargs)


class InMemoryHealthRepository:
    async def ping(self) -> bool: return True
