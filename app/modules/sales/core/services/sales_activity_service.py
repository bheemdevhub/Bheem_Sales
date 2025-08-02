from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.modules.sales.core.schemas.sales_activity_schemas import (
    SalesActivityCreate, SalesActivityUpdate
)
from app.modules.sales.core.models.sales_activity import SalesActivity
from typing import List, Tuple, Optional

class SalesActivityService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_activity(self, activity_data: SalesActivityCreate) -> SalesActivity:
        activity = SalesActivity(**activity_data.dict())
        self.db.add(activity)
        await self.db.commit()
        await self.db.refresh(activity)
        return activity

    async def list_activities(self, skip: int = 0, limit: int = 100) -> Tuple[List[SalesActivity], int]:
        # Get total count
        count_result = await self.db.execute(select(SalesActivity))
        total = len(count_result.scalars().all())
        
        # Get paginated results
        result = await self.db.execute(select(SalesActivity).offset(skip).limit(limit))
        activities = result.scalars().all()
        return activities, total

    async def get_activity(self, activity_id: UUID) -> Optional[SalesActivity]:
        result = await self.db.execute(select(SalesActivity).where(SalesActivity.id == activity_id))
        return result.scalar_one_or_none()

    async def update_activity(self, activity_id: UUID, activity_data: SalesActivityUpdate) -> Optional[SalesActivity]:
        activity = await self.get_activity(activity_id)
        if not activity:
            return None
        for key, value in activity_data.dict(exclude_unset=True).items():
            setattr(activity, key, value)
        await self.db.commit()
        await self.db.refresh(activity)
        return activity

    async def delete_activity(self, activity_id: UUID) -> bool:
        activity = await self.get_activity(activity_id)
        if not activity:
            return False
        await self.db.delete(activity)
        await self.db.commit()
        return True

    async def complete_activity(self, activity_id: UUID) -> Optional[SalesActivity]:
        activity = await self.get_activity(activity_id)
        if not activity:
            return None
        activity.is_completed = True
        await self.db.commit()
        await self.db.refresh(activity)
        return activity
