from typing import Optional, List, Dict, Any, Union
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field, validator, root_validator
from app.modules.sales.core.models.sales_models import InvoiceStatus


# Base Schema for Sales Invoice Line Items
class SalesInvoiceLineItemBase(BaseModel):
    line_number: int
    sku_id: UUID
    product_code: Optional[str]
    product_name: str
    description: Optional[str]
    quantity: float
    unit_price: float
    discount_percentage: Optional[float] = 0.0
    discount_amount: Optional[float] = 0.0
    line_total: float
    tax_code: Optional[str]
    tax_rate: Optional[float] = 0.0
    tax_amount: Optional[float] = 0.0
    attributes: Optional[dict] = None


# Create Schema for Sales Invoice Line Items
class SalesInvoiceLineItemCreate(SalesInvoiceLineItemBase):
    pass


# Update Schema for Sales Invoice Line Items
class SalesInvoiceLineItemUpdate(BaseModel):
    sku_id: Optional[UUID] = None
    product_code: Optional[str] = None
    product_name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    discount_percentage: Optional[float] = None
    discount_amount: Optional[float] = None
    tax_code: Optional[str] = None
    tax_rate: Optional[float] = None
    revenue_account_id: Optional[UUID] = None
    attributes: Optional[Dict[str, Any]] = None


# Response Schema for Sales Invoice Line Items
class SalesInvoiceLineItemResponse(BaseModel):
    id: UUID
    line_number: int
    sku_id: UUID
    product_code: Optional[str]
    product_name: str
    description: Optional[str]
    quantity: float
    unit_price: float
    discount_percentage: float
    discount_amount: float
    line_total: float
    tax_code: Optional[str]
    tax_rate: float
    tax_amount: float
    attributes: Optional[dict]

    class Config:
        from_attributes = True


# Base Schema for Sales Invoices
class SalesInvoiceBase(BaseModel):
    invoice_number: str = Field(..., min_length=1, max_length=50)
    invoice_date: date
    due_date: date
    status: InvoiceStatus = InvoiceStatus.DRAFT
    subtotal: Optional[float] = 0.0
    tax_amount: Optional[float] = 0.0
    discount_amount: Optional[float] = 0.0
    total_amount: Optional[float] = 0.0
    paid_amount: Optional[float] = 0.0
    balance_due: Optional[float] = 0.0
    currency_id: Optional[UUID] = None
    payment_terms: Optional[int] = 30
    late_fee_rate: Optional[float] = Field(0.0, ge=0)
    notes: Optional[str] = None

    @validator('due_date')
    def due_date_after_invoice_date(cls, v, values):
        if 'invoice_date' in values and v < values['invoice_date']:
            raise ValueError('Due date must be after invoice date')
        return v


# Create Schema for Sales Invoices
class SalesInvoiceCreate(SalesInvoiceBase):
    company_id: UUID
    customer_id: UUID
    sales_order_id: Optional[UUID] = None
    line_items: List[SalesInvoiceLineItemCreate] = Field(..., min_items=1)


# Update Schema for Sales Invoices
class SalesInvoiceUpdate(BaseModel):
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    status: Optional[InvoiceStatus] = None
    currency_id: Optional[UUID] = None
    payment_terms: Optional[int] = None
    late_fee_rate: Optional[float] = None
    notes: Optional[str] = None


# Response Schema for Sales Invoices
class SalesInvoiceResponse(BaseModel):
    id: UUID
    company_id: UUID
    customer_id: UUID
    sales_order_id: Optional[UUID]
    invoice_number: str
    invoice_date: date
    due_date: date
    status: InvoiceStatus
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    paid_amount: float
    balance_due: float
    currency_id: UUID
    payment_terms: int
    late_fee_rate: float
    notes: Optional[str]
    line_items: List[SalesInvoiceLineItemResponse]

    class Config:
        from_attributes = True

# Detail Response Schema for Sales Invoices with Line Items
class SalesInvoiceDetailResponse(SalesInvoiceResponse):
    line_items: List[SalesInvoiceLineItemResponse] = []
    customer_name: Optional[str] = None
    payment_history: List[Dict[str, Any]] = []
    days_overdue: Optional[int] = None


# Search Parameters for Sales Invoices
class SalesInvoiceSearchParams(BaseModel):
    query: Optional[str] = None
    status: Optional[InvoiceStatus] = None
    customer_id: Optional[str] = None
    created_after: Optional[date] = None
    created_before: Optional[date] = None
    due_after: Optional[date] = None
    due_before: Optional[date] = None
    min_total: Optional[float] = None
    max_total: Optional[float] = None
    is_overdue: Optional[bool] = None
    is_paid: Optional[bool] = None
    sort_by: Optional[str] = "invoice_date"
    sort_desc: Optional[bool] = True
    limit: Optional[int] = 100
    offset: Optional[int] = 0


# Paginated Response for Sales Invoices
class SalesInvoicePaginatedResponse(BaseModel):
    items: List[SalesInvoiceResponse]
    total: int
    limit: int
    offset: int
    hasMore: bool


# Status Update Schema for Sales Invoices
class SalesInvoiceStatusUpdate(BaseModel):
    status: InvoiceStatus
    notes: Optional[str] = None


# Apply Payment Schema
class SalesInvoicePaymentApplication(BaseModel):
    payment_id: UUID
    amount: float = Field(..., gt=0)
    payment_date: Optional[date] = None
    notes: Optional[str] = None
