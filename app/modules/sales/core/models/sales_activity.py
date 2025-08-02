from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4
from datetime import datetime, date
from app.shared.models import ActivityType, ActivityStatus

Base = declarative_base()

class SalesActivity(Base):
    __tablename__ = "sales_activities"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    activity_type = Column(Enum(ActivityType), nullable=False)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    assigned_to = Column(PG_UUID(as_uuid=True), nullable=True)
    scheduled_date = Column(DateTime, nullable=True) 
    due_date = Column(DateTime, nullable=True)
    status = Column(Enum(ActivityStatus), nullable=False, default=ActivityStatus.PENDING)
    is_completed = Column(Boolean, default=False)
    completion_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    priority = Column(String(20), default="MEDIUM")
    company_id = Column(PG_UUID(as_uuid=True), nullable=False)
    created_by = Column(PG_UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

