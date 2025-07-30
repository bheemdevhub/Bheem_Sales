from typing import Optional, List, Dict, Any, Union
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from bheem_core.modules.sales.core.models.sales_models import PaymentMethod, PaymentStatus


# Base Schema for Customer Payments
class CustomerPaymentBase(BaseModel):
    payment_reference: str = Field(..., min_length=1, max_length=50)
    payment_date: date
    amount: float = Field(..., gt=0)
    payment_method: PaymentMethod
    status: PaymentStatus = PaymentStatus.PENDING
    transaction_id: Optional[str] = None
    bank_reference: Optional[str] = None
    notes: Optional[str] = None
    currency_id: Optional[UUID] = None


# Create Schema for Customer Payments
class CustomerPaymentCreate(CustomerPaymentBase):
    company_id: UUID
    customer_id: str
    invoice_id: Optional[UUID] = None  # Can be None for advance payments


# Update Schema for Customer Payments
class CustomerPaymentUpdate(BaseModel):
    payment_date: Optional[date] = None
    amount: Optional[float] = None
    payment_method: Optional[PaymentMethod] = None
    status: Optional[PaymentStatus] = None
    transaction_id: Optional[str] = None
    bank_reference: Optional[str] = None
    notes: Optional[str] = None
    currency_id: Optional[UUID] = None


# Response Schema for Customer Payments
class CustomerPaymentResponse(CustomerPaymentBase):
    id: UUID
    company_id: UUID
    customer_id: str
    invoice_id: Optional[UUID] = None
    accounting_journal_entry_id: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


# Detail Response Schema for Customer Payments with Related Data
class CustomerPaymentDetailResponse(CustomerPaymentResponse):
    customer_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    invoice_total: Optional[float] = None
    allocated_amount: Optional[float] = None
    unallocated_amount: Optional[float] = None
    

# Search Parameters for Customer Payments
class CustomerPaymentSearchParams(BaseModel):
    query: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    status: Optional[PaymentStatus] = None
    customer_id: Optional[str] = None
    invoice_id: Optional[UUID] = None
    created_after: Optional[date] = None
    created_before: Optional[date] = None
    payment_after: Optional[date] = None
    payment_before: Optional[date] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    is_allocated: Optional[bool] = None
    sort_by: Optional[str] = "payment_date"
    sort_desc: Optional[bool] = True
    limit: Optional[int] = 100
    offset: Optional[int] = 0


# Paginated Response for Customer Payments
class CustomerPaymentPaginatedResponse(BaseModel):
    items: List[CustomerPaymentResponse]
    total: int
    limit: int
    offset: int
    hasMore: bool


# Status Update Schema for Customer Payments
class CustomerPaymentStatusUpdate(BaseModel):
    status: PaymentStatus
    notes: Optional[str] = None


# Allocation Schema for Customer Payments
class CustomerPaymentAllocation(BaseModel):
    invoice_id: UUID = Field(...)
    amount: float = Field(..., gt=0)
    allocation_date: Optional[date] = None
    notes: Optional[str] = None
    
    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Allocation amount must be greater than zero')
        return v

