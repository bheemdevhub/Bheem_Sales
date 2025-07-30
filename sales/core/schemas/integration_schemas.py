from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


# Integration Configuration Schemas
class IntegrationConfigCreate(BaseModel):
    integration_type: str
    config_data: Dict[str, Any]
    company_id: UUID

class IntegrationConfigUpdate(BaseModel):
    config_data: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class IntegrationConfigResponse(BaseModel):
    id: UUID
    integration_type: str
    config_data: Dict[str, Any]
    is_active: bool
    company_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# Webhook Configuration Schemas
class WebhookConfigCreate(BaseModel):
    webhook_url: str
    events: List[str]
    company_id: UUID

class WebhookConfigResponse(BaseModel):
    id: UUID
    webhook_url: str
    events: List[str]
    is_active: bool
    company_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class WebhookEventResponse(BaseModel):
    id: UUID
    event_type: str
    payload: Dict[str, Any]
    status: str
    created_at: datetime


# External Sync Schemas
class ExternalSyncRequest(BaseModel):
    sync_type: str
    entity_type: str
    entity_ids: Optional[List[UUID]] = None
    company_id: UUID

class ExternalSyncResponse(BaseModel):
    sync_id: UUID
    status: str
    synced_count: int
    errors: List[Dict[str, Any]] = []
    started_at: datetime


# Integration Health Schema
class IntegrationHealthResponse(BaseModel):
    integration_type: str
    status: str
    last_sync: Optional[datetime] = None
    error_count: int
    health_score: float

