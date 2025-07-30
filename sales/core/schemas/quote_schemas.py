from typing import Optional, List, Dict, Any, Union
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field, validator, root_validator
from bheem_core.modules.sales.core.models.sales_models import QuoteStatus


# Base Schema for Quote Line Items
class QuoteLineItemBase(BaseModel):
    line_number: int = Field(..., ge=1)
    product_id: Optional[UUID] = None
    product_code: Optional[str] = None
    product_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    quantity: float = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)
    discount_percentage: Optional[float] = Field(0.0, ge=0, le=100)
    discount_amount: Optional[float] = Field(0.0, ge=0)
    tax_code: Optional[str] = None
    tax_rate: Optional[float] = Field(0.0, ge=0)
    attributes: Optional[Dict[str, Any]] = None


# Create Schema for Quote Line Items
class QuoteLineItemCreate(QuoteLineItemBase):
    pass


# Update Schema for Quote Line Items
class QuoteLineItemUpdate(BaseModel):
    product_id: Optional[UUID] = None
    product_code: Optional[str] = None
    product_name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    discount_percentage: Optional[float] = None
    discount_amount: Optional[float] = None
    tax_code: Optional[str] = None
    tax_rate: Optional[float] = None
    attributes: Optional[Dict[str, Any]] = None


# Response Schema for Quote Line Items
class QuoteLineItemResponse(QuoteLineItemBase):
    id: UUID
    quote_id: UUID
    line_total: float
    tax_amount: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


# Base Schema for Quotes
class QuoteBase(BaseModel):
    quote_number: str = Field(..., min_length=1, max_length=50)
    quote_date: date
    valid_until: date
    status: QuoteStatus = QuoteStatus.DRAFT
    subtotal: Optional[float] = 0.0
    tax_amount: Optional[float] = 0.0
    discount_amount: Optional[float] = 0.0
    total_amount: Optional[float] = 0.0
    currency_id: Optional[UUID] = None
    notes: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    
    @validator('valid_until')
    def valid_until_after_quote_date(cls, v, values):
        if 'quote_date' in values and v < values['quote_date']:
            raise ValueError('Valid until date must be after quote date')
        return v


# Create Schema for Quotes
class QuoteCreate(QuoteBase):
    company_id: UUID
    customer_id: str
    line_items: List[QuoteLineItemCreate] = Field(..., min_items=1)


# Update Schema for Quotes
class QuoteUpdate(BaseModel):
    quote_date: Optional[date] = None
    valid_until: Optional[date] = None
    status: Optional[QuoteStatus] = None
    currency_id: Optional[UUID] = None
    notes: Optional[str] = None
    terms_and_conditions: Optional[str] = None


# Response Schema for Quotes
class QuoteResponse(QuoteBase):
    id: UUID
    company_id: UUID
    customer_id: str
    sent_date: Optional[datetime] = None
    viewed_date: Optional[datetime] = None
    accepted_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


# Detail Response Schema for Quotes with Line Items
class QuoteDetailResponse(QuoteResponse):
    line_items: List[QuoteLineItemResponse] = []
    customer_name: Optional[str] = None
    converted_to_order: bool = False


# Search Parameters for Quotes
class QuoteSearchParams(BaseModel):
    query: Optional[str] = None
    status: Optional[QuoteStatus] = None
    customer_id: Optional[str] = None
    created_after: Optional[date] = None
    created_before: Optional[date] = None
    valid_after: Optional[date] = None
    valid_before: Optional[date] = None
    min_total: Optional[float] = None
    max_total: Optional[float] = None
    sort_by: Optional[str] = "quote_date"
    sort_desc: Optional[bool] = True
    limit: Optional[int] = 100
    offset: Optional[int] = 0


# Paginated Response for Quotes
class QuotePaginatedResponse(BaseModel):
    items: List[QuoteResponse]
    total: int
    limit: int
    offset: int
    hasMore: bool


# Status Update Schema for Quotes
class QuoteStatusUpdate(BaseModel):
    status: QuoteStatus
    notes: Optional[str] = None


# Convert Quote to Order Schema
class QuoteToOrderConversion(BaseModel):
    order_number: str = Field(..., min_length=1, max_length=50)
    order_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None
    shipping_address: Optional[Dict[str, str]] = None
    shipping_method: Optional[str] = None
    notes: Optional[str] = None

