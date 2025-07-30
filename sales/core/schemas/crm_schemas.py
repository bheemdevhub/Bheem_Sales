from typing import Optional, List, Dict, Any
from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr


# Base CRM Account Schema
class CRMAccountBase(BaseModel):
    account_name: str = Field(..., min_length=1, max_length=255)
    account_type: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    
class CRMAccountCreate(CRMAccountBase):
    company_id: UUID

class CRMAccountUpdate(BaseModel):
    account_name: Optional[str] = None
    account_type: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class CRMAccountResponse(CRMAccountBase):
    id: UUID
    company_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CRMAccountPaginatedResponse(BaseModel):
    items: List[CRMAccountResponse]
    total: int
    limit: int
    offset: int
    has_more: bool


# Base CRM Contact Schema
class CRMContactBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    
class CRMContactCreate(CRMContactBase):
    account_id: UUID
    company_id: UUID

class CRMContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    title: Optional[str] = None

class CRMContactResponse(CRMContactBase):
    id: UUID
    account_id: UUID
    company_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CRMContactPaginatedResponse(BaseModel):
    items: List[CRMContactResponse]
    total: int
    limit: int
    offset: int
    has_more: bool


# CRM Interaction Schema
class CRMInteractionCreate(BaseModel):
    interaction_type: str
    subject: str
    description: Optional[str] = None
    contact_id: Optional[UUID] = None
    account_id: Optional[UUID] = None
    company_id: UUID

class CRMInteractionResponse(BaseModel):
    id: UUID
    interaction_type: str
    subject: str
    description: Optional[str] = None
    contact_id: Optional[UUID] = None
    account_id: Optional[UUID] = None
    company_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# CRM Pipeline Schema
class CRMPipelineResponse(BaseModel):
    pipeline_name: str
    total_value: float
    stage_summary: Dict[str, Any] = {}
    

# CRM Dashboard Schema
class CRMDashboardResponse(BaseModel):
    total_accounts: int
    total_contacts: int
    total_opportunities: int
    pipeline_value: float
    recent_activities: List[Dict[str, Any]] = []


# CRM Lead Scoring Schema
class CRMLeadScoringResponse(BaseModel):
    lead_id: UUID
    score: float
    factors: List[str] = []
    recommendations: List[str] = []

