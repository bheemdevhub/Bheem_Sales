from typing import Optional, List, Dict, Any, Union
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field, validator, root_validator
from bheem_core.modules.sales.core.models.sales_models import OrderStatus


# Base Schema for Sales Order Line Items
class SalesOrderLineItemBase(BaseModel):
    line_number: int = Field(..., ge=1)
    product_id: Optional[UUID] = None
    product_code: Optional[str] = None
    product_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    quantity_ordered: float = Field(..., gt=0)
    quantity_shipped: Optional[float] = Field(0.0, ge=0)
    quantity_invoiced: Optional[float] = Field(0.0, ge=0)
    unit_price: float = Field(..., ge=0)
    discount_percentage: Optional[float] = Field(0.0, ge=0, le=100)
    discount_amount: Optional[float] = Field(0.0, ge=0)
    tax_code: Optional[str] = None
    tax_rate: Optional[float] = Field(0.0, ge=0)
    expected_ship_date: Optional[date] = None
    actual_ship_date: Optional[date] = None
    attributes: Optional[Dict[str, Any]] = None


# Create Schema for Sales Order Line Items
class SalesOrderLineItemCreate(SalesOrderLineItemBase):
    pass


# Update Schema for Sales Order Line Items
class SalesOrderLineItemUpdate(BaseModel):
    product_id: Optional[UUID] = None
    product_code: Optional[str] = None
    product_name: Optional[str] = None
    description: Optional[str] = None
    quantity_ordered: Optional[float] = None
    quantity_shipped: Optional[float] = None
    quantity_invoiced: Optional[float] = None
    unit_price: Optional[float] = None
    discount_percentage: Optional[float] = None
    discount_amount: Optional[float] = None
    tax_code: Optional[str] = None
    tax_rate: Optional[float] = None
    expected_ship_date: Optional[date] = None
    actual_ship_date: Optional[date] = None
    attributes: Optional[Dict[str, Any]] = None


# Response Schema for Sales Order Line Items
class SalesOrderLineItemResponse(SalesOrderLineItemBase):
    id: UUID
    sales_order_id: UUID
    line_total: float
    tax_amount: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


# Base Schema for Sales Orders
class SalesOrderBase(BaseModel):
    order_number: str = Field(..., min_length=1, max_length=50)
    order_date: date
    expected_delivery_date: Optional[date] = None
    status: OrderStatus = OrderStatus.DRAFT
    subtotal: Optional[float] = 0.0
    tax_amount: Optional[float] = 0.0
    shipping_amount: Optional[float] = 0.0
    discount_amount: Optional[float] = 0.0
    total_amount: Optional[float] = 0.0
    currency_id: Optional[UUID] = None
    shipping_address: Optional[Dict[str, str]] = None
    shipping_method: Optional[str] = None
    tracking_number: Optional[str] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None


# Create Schema for Sales Orders
class SalesOrderCreate(SalesOrderBase):
    company_id: UUID
    customer_id: str
    quote_id: Optional[UUID] = None
    line_items: List[SalesOrderLineItemCreate] = Field(..., min_items=1)


# Update Schema for Sales Orders
class SalesOrderUpdate(BaseModel):
    order_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None
    status: Optional[OrderStatus] = None
    shipping_amount: Optional[float] = None
    currency_id: Optional[UUID] = None
    shipping_address: Optional[Dict[str, str]] = None
    shipping_method: Optional[str] = None
    tracking_number: Optional[str] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None


# Response Schema for Sales Orders
class SalesOrderResponse(SalesOrderBase):
    id: UUID
    company_id: UUID
    customer_id: str
    quote_id: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


# Detail Response Schema for Sales Orders with Line Items
class SalesOrderDetailResponse(SalesOrderResponse):
    line_items: List[SalesOrderLineItemResponse] = []
    customer_name: Optional[str] = None
    invoiced_amount: float = 0.0
    remaining_to_invoice: float = 0.0
    invoices_count: int = 0


# Search Parameters for Sales Orders
class SalesOrderSearchParams(BaseModel):
    query: Optional[str] = None
    status: Optional[OrderStatus] = None
    customer_id: Optional[str] = None
    created_after: Optional[date] = None
    created_before: Optional[date] = None
    expected_delivery_after: Optional[date] = None
    expected_delivery_before: Optional[date] = None
    min_total: Optional[float] = None
    max_total: Optional[float] = None
    has_tracking: Optional[bool] = None
    has_invoices: Optional[bool] = None
    sort_by: Optional[str] = "order_date"
    sort_desc: Optional[bool] = True
    limit: Optional[int] = 100
    offset: Optional[int] = 0


# Paginated Response for Sales Orders
class SalesOrderPaginatedResponse(BaseModel):
    items: List[SalesOrderResponse]
    total: int
    limit: int
    offset: int
    hasMore: bool


# Status Update Schema for Sales Orders
class SalesOrderStatusUpdate(BaseModel):
    status: OrderStatus
    notes: Optional[str] = None


# Fulfillment Update Schema for Sales Orders
class SalesOrderFulfillmentUpdate(BaseModel):
    line_item_id: UUID
    quantity_shipped: float = Field(..., gt=0)
    actual_ship_date: Optional[date] = None
    tracking_number: Optional[str] = None
    shipping_method: Optional[str] = None
    notes: Optional[str] = None


# Create Invoice from Order Schema
class SalesOrderToInvoiceConversion(BaseModel):
    invoice_number: str = Field(..., min_length=1, max_length=50)
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    line_items: Optional[List[UUID]] = None  # List of line item IDs to include, if None includes all
    notes: Optional[str] = None

