from typing import Optional, List, Dict, Any, Union
from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, validator, root_validator
from app.modules.sales.core.models.sales_models import CustomerType, CustomerStatus


# Base Schemas
class CustomerBase(BaseModel):
    customer_code: str = Field(..., min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    business_name: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    customer_type: CustomerType = Field(CustomerType.INDIVIDUAL)
    customer_status: CustomerStatus = Field(CustomerStatus.PROSPECT)
    tax_id: Optional[str] = Field(None, max_length=50)
    credit_limit: Optional[float] = Field(0.0, ge=0)
    payment_terms: Optional[int] = Field(30, ge=0)
    currency_id: Optional[UUID] = None
    preferred_communication: Optional[str] = Field("EMAIL", max_length=50)
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
        if 'customer_type' in values and values['customer_type'] == CustomerType.BUSINESS and not v:
            raise ValueError('Business name is required for business customers')
        return v
    
    @validator('first_name', 'last_name')
    def names_required_for_individuals(cls, v, values):
        if 'customer_type' in values and values['customer_type'] == CustomerType.INDIVIDUAL and not v:
            raise ValueError('First name and last name are required for individual customers')
        return v


# Create Schema
class CustomerCreate(CustomerBase):
    # company_id: UUID
    sales_rep_id: Optional[UUID] = None


# Update Schema
class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    business_name: Optional[str] = None
    industry: Optional[str] = None
    customer_type: Optional[CustomerType] = None
    customer_status: Optional[CustomerStatus] = None
    tax_id: Optional[str] = None
    credit_limit: Optional[float] = None
    payment_terms: Optional[int] = None
    currency_id: Optional[UUID] = None
    sales_rep_id: Optional[UUID] = None
    preferred_communication: Optional[str] = None
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
class CustomerResponse(CustomerBase):
    id: str
    company_id: UUID
    sales_rep_id: Optional[UUID] = None
    customer_since: Optional[date] = None
    last_purchase_date: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


# Detail Response Schema with additional relationships
class CustomerDetailResponse(CustomerResponse):
    total_orders: int = 0
    total_invoiced: float = 0
    total_paid: float = 0
    balance_due: float = 0
    overall_rating: float = 0


# Search Parameters
class CustomerSearchParams(BaseModel):
    query: Optional[str] = None
    customer_type: Optional[CustomerType] = None
    customer_status: Optional[CustomerStatus] = None
    sales_rep_id: Optional[UUID] = None
    created_after: Optional[date] = None
    created_before: Optional[date] = None
    min_credit_limit: Optional[float] = None
    max_credit_limit: Optional[float] = None
    industry: Optional[str] = None
    tags: Optional[List[str]] = None
    sort_by: Optional[str] = "customer_code"
    sort_desc: Optional[bool] = False
    limit: Optional[int] = 100
    offset: Optional[int] = 0


# Paginated Response
class CustomerPaginatedResponse(BaseModel):
    items: List[CustomerResponse]
    total: int
    limit: int
    offset: int
    hasMore: bool
    
    
# Customer Activity
class CustomerActivity(BaseModel):
    activity_type: str
    subject: str
    description: Optional[str] = None
    assigned_to: Optional[UUID] = None
    scheduled_date: Optional[datetime] = None
    due_date: Optional[date] = None
    is_completed: bool = False
    
    
# Customer Analytics
class CustomerAnalytics(BaseModel):
    customer_id: str
    total_orders: int = 0
    total_invoiced: float = 0
    total_paid: float = 0
    last_purchase_date: Optional[date] = None
    average_order_value: float = 0
    purchase_frequency: float = 0  # Average days between orders
    customer_lifetime_value: float = 0
    payment_performance: float = 0  # Ratio of on-time payments
