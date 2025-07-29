from typing import Optional, List, Dict, Any, Union
from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, validator
from app.modules.sales.core.models.sales_models import CustomerType, CustomerStatus


# Base Schemas
class VendorBase(BaseModel):
    vendor_code: str = Field(..., min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    business_name: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    vendor_type: CustomerType = Field(CustomerType.BUSINESS)
    vendor_status: CustomerStatus = Field(CustomerStatus.ACTIVE)
    tax_id: Optional[str] = Field(None, max_length=50)
    credit_limit: Optional[float] = Field(0.0, ge=0)
    payment_terms: Optional[int] = Field(30, ge=0)
    currency_id: Optional[UUID] = None
    quality_rating: Optional[float] = Field(0.0, ge=0, le=5.0)
    delivery_rating: Optional[float] = Field(0.0, ge=0, le=5.0)
    service_rating: Optional[float] = Field(0.0, ge=0, le=5.0)
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
        if 'vendor_type' in values and values['vendor_type'] == CustomerType.BUSINESS and not v:
            raise ValueError('Business name is required for business vendors')
        return v
    
    @validator('first_name', 'last_name')
    def names_required_for_individuals(cls, v, values):
        if 'vendor_type' in values and values['vendor_type'] == CustomerType.INDIVIDUAL and not v:
            raise ValueError('First name and last name are required for individual vendors')
        return v


# Create Schema
class VendorCreate(VendorBase):
    company_id: UUID
    procurement_rep_id: Optional[UUID] = None


# Update Schema
class VendorUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    business_name: Optional[str] = None
    industry: Optional[str] = None
    vendor_type: Optional[CustomerType] = None
    vendor_status: Optional[CustomerStatus] = None
    tax_id: Optional[str] = None
    credit_limit: Optional[float] = None
    payment_terms: Optional[int] = None
    currency_id: Optional[UUID] = None
    procurement_rep_id: Optional[UUID] = None
    quality_rating: Optional[float] = None
    delivery_rating: Optional[float] = None
    service_rating: Optional[float] = None
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
class VendorResponse(VendorBase):
    id: str
    company_id: UUID
    procurement_rep_id: Optional[UUID] = None
    vendor_since: Optional[date] = None
    last_purchase_date: Optional[date] = None
    total_purchases_value: Optional[float] = 0.0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


# Detail Response Schema with additional relationships
class VendorDetailResponse(VendorResponse):
    average_rating: Dict[str, float] = Field(default_factory=lambda: {
        'quality': 0.0, 
        'delivery': 0.0, 
        'service': 0.0
    })
    total_orders: int = 0


# Search Parameters
class VendorSearchParams(BaseModel):
    query: Optional[str] = None
    vendor_type: Optional[CustomerType] = None
    vendor_status: Optional[CustomerStatus] = None
    procurement_rep_id: Optional[UUID] = None
    created_after: Optional[date] = None
    created_before: Optional[date] = None
    min_quality_rating: Optional[float] = None
    max_quality_rating: Optional[float] = None
    min_delivery_rating: Optional[float] = None
    max_delivery_rating: Optional[float] = None
    industry: Optional[str] = None
    tags: Optional[List[str]] = None
    sort_by: Optional[str] = "vendor_code"
    sort_desc: Optional[bool] = False
    limit: Optional[int] = 100
    offset: Optional[int] = 0


# Paginated Response
class VendorPaginatedResponse(BaseModel):
    items: List[VendorResponse]
    total: int
    limit: int
    offset: int
    hasMore: bool
    
    
# Vendor Activity
class VendorActivity(BaseModel):
    activity_type: str
    subject: str
    description: Optional[str] = None
    assigned_to: Optional[UUID] = None
    scheduled_date: Optional[datetime] = None
    due_date: Optional[date] = None
    is_completed: bool = False
    
    
# Vendor Rating
class VendorRatingUpdate(BaseModel):
    quality_rating: Optional[float] = Field(None, ge=0, le=5)
    delivery_rating: Optional[float] = Field(None, ge=0, le=5)
    service_rating: Optional[float] = Field(None, ge=0, le=5)
    notes: Optional[str] = None
