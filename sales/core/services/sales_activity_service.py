from sqlalchemy.orm import Session
from uuid import UUID
from bheem_core.modules.sales.core.schemas.sales_activity_schemas import (
    SalesActivityCreate, SalesActivityUpdate
)
from bheem_core.modules.sales.core.models.sales_activity import SalesActivity
from typing import List, Tuple, Optional

class SalesActivityService:
    def __init__(self, db: Session):
        self.db = db

    def create_activity(self, activity_data: SalesActivityCreate) -> SalesActivity:
        activity = SalesActivity(**activity_data.dict())
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        return activity

    def list_activities(self, skip: int = 0, limit: int = 100) -> Tuple[List[SalesActivity], int]:
        query = self.db.query(SalesActivity)
        total = query.count()
        activities = query.offset(skip).limit(limit).all()
        return activities, total

    def get_activity(self, activity_id: UUID) -> Optional[SalesActivity]:
        return self.db.query(SalesActivity).filter(SalesActivity.id == activity_id).first()

    def update_activity(self, activity_id: UUID, activity_data: SalesActivityUpdate) -> Optional[SalesActivity]:
        activity = self.get_activity(activity_id)
        if not activity:
            return None
        for key, value in activity_data.dict(exclude_unset=True).items():
            setattr(activity, key, value)
        self.db.commit()
        self.db.refresh(activity)
        return activity

    def delete_activity(self, activity_id: UUID) -> bool:
        activity = self.get_activity(activity_id)
        if not activity:
            return False
        self.db.delete(activity)
        self.db.commit()
        return True

    def complete_activity(self, activity_id: UUID) -> Optional[SalesActivity]:
        activity = self.get_activity(activity_id)
        if not activity:
            return None
        activity.is_completed = True
        self.db.commit()
        self.db.refresh(activity)
        return activity

