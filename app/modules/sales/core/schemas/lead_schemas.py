from typing import Optional, List, Dict, Any, Union
from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, validator
from app.modules.sales.core.models.sales_models import CustomerType
from app.modules.sales.core.models.sales_models import TagCategory, Tag

# Base Schemas
class LeadBase(BaseModel):
    lead_code: str = Field(..., min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    business_name: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    lead_type: CustomerType = Field(CustomerType.INDIVIDUAL)
    source: Optional[str] = Field(None, max_length=100)
    lead_status: str = Field("NEW", max_length=50)
    lead_score: Optional[int] = Field(0, ge=0, le=100)
    qualification_status: str = Field("UNQUALIFIED", max_length=50)
    expected_close_date: Optional[date] = None
    estimated_value: Optional[float] = Field(0.0, ge=0)
    lead_notes: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    
    # Address fields
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    
    @validator('business_name')
    def business_name_required_for_business(cls, v, values):
        if 'lead_type' in values and values['lead_type'] == CustomerType.BUSINESS and not v:
            raise ValueError('Business name is required for business leads')
        return v
    
    @validator('first_name', 'last_name')
    def names_required_for_individuals(cls, v, values):
        if 'lead_type' in values and values['lead_type'] == CustomerType.INDIVIDUAL and not v:
            raise ValueError('First name and last name are required for individual leads')
        return v

class TagInput(BaseModel):
    tag_value: str
    tag_category: TagCategory
    tag_color: Optional[str] = "#000000"

# Create Schema
class LeadCreate(BaseModel):
    lead_code: str
    first_name: str
    last_name: str
    source: Optional[str] = None
    lead_type: Optional[str] = "INDIVIDUAL"
    lead_status: Optional[str] = "NEW"
    business_name: Optional[str] = None
    industry: Optional[str] = None
    lead_score: Optional[int] = 0
    qualification_status: Optional[str] = "UNQUALIFIED"
    sales_rep_id: Optional[UUID] = None
    first_contact_date: Optional[date] = None
    last_contact_date: Optional[date] = None
    expected_close_date: Optional[date] = None
    estimated_value: Optional[float] = 0.0
    tags: Optional[List[TagInput]] = []
    custom_fields: Optional[dict] = {}
    lead_notes: Optional[str] = None
    company_id: UUID

    # Extra: For Contact creation (NOT part of Lead model)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

# Update Schema
class LeadUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    business_name: Optional[str] = None
    industry: Optional[str] = None
    lead_type: Optional[CustomerType] = None
    source: Optional[str] = None
    lead_status: Optional[str] = None
    lead_score: Optional[int] = None
    qualification_status: Optional[str] = None
    sales_rep_id: Optional[UUID] = None
    expected_close_date: Optional[date] = None
    estimated_value: Optional[float] = None
    lead_notes: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    
    # Address fields
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


# Response Schema
class LeadResponse(LeadBase):
    id: str
    company_id: UUID
    sales_rep_id: Optional[UUID] = None
    first_contact_date: Optional[date] = None
    last_contact_date: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


# Detail Response Schema with additional relationships
class LeadDetailResponse(LeadResponse):
    activities_count: int = 0
    converted_to_customer_id: Optional[str] = None
    conversion_date: Optional[date] = None


# Search Parameters
class LeadSearchParams(BaseModel):
    query: Optional[str] = None
    lead_type: Optional[CustomerType] = None
    lead_status: Optional[str] = None
    qualification_status: Optional[str] = None
    sales_rep_id: Optional[UUID] = None
    source: Optional[str] = None
    created_after: Optional[date] = None
    created_before: Optional[date] = None
    min_lead_score: Optional[int] = None
    max_lead_score: Optional[int] = None
    min_estimated_value: Optional[float] = None
    max_estimated_value: Optional[float] = None
    industry: Optional[str] = None
    tags: Optional[List[str]] = None
    sort_by: Optional[str] = "lead_code"
    sort_desc: Optional[bool] = False
    limit: Optional[int] = 100
    offset: Optional[int] = 0


# Paginated Response
class LeadPaginatedResponse(BaseModel):
    items: List[LeadResponse]
    total: int
    limit: int
    offset: int
    hasMore: bool


# Lead Activity
class LeadActivity(BaseModel):
    activity_type: str
    subject: str
    description: Optional[str] = None
    assigned_to: Optional[UUID] = None
    scheduled_date: Optional[datetime] = None
    due_date: Optional[date] = None
    is_completed: bool = False


# Lead Conversion
class LeadConversion(BaseModel):
    customer_code: str = Field(..., min_length=3, max_length=50)
    customer_type: CustomerType
    customer_status: str = "ACTIVE"


# Lead Analytics
class LeadAnalytics(BaseModel):
    total_leads: int = 0
    new_leads: int = 0
    qualified_leads: int = 0
    conversion_rate: float = 0  # Percentage of leads converted to customers
    average_qualification_time: float = 0  # Average days to qualify
    average_conversion_time: float = 0  # Average days to convert
    average_lead_value: float = 0
    lead_sources: Dict[str, int] = {}  # Count by source
