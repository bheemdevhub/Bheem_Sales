from typing import Optional, List, Literal
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field, validator, root_validator
from app.modules.sales.core.models.sales_models import OrderStatus


class SalesOrderLineItemCreate(BaseModel):
    sku_id: UUID
    product_code: Optional[str]
    product_name: str
    description: Optional[str] = None

    quantity_ordered: Decimal
    unit_price: Decimal
    discount_percentage: Optional[Decimal] = 0
    discount_amount: Optional[Decimal] = 0
    line_total: Decimal

    tax_code: Optional[str] = None
    tax_rate: Optional[Decimal] = 0
    tax_amount: Optional[Decimal] = 0

    expected_ship_date: Optional[date] = None
    attributes: Optional[dict] = {}

# ----- Sales Order Schema -----
class SalesOrderCreate(BaseModel):
    customer_id: UUID
    quote_id: Optional[UUID] = None
    order_number: str
    order_date: date
    expected_delivery_date: Optional[date] = None
    status: Optional[str] = "DRAFT"

    subtotal: Decimal
    tax_amount: Decimal
    shipping_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    currency_id: UUID

    shipping_address: Optional[dict] = None
    shipping_method: Optional[str] = None
    tracking_number: Optional[str] = None

    notes: Optional[str] = None
    internal_notes: Optional[str] = None

    line_items: List[SalesOrderLineItemCreate]

class SalesOrderLineItemResponse(BaseModel):
    id: UUID
    line_number: int
    sku_id: UUID
    product_code: Optional[str]
    product_name: str
    description: Optional[str]

    quantity_ordered: Decimal
    quantity_shipped: Decimal
    quantity_invoiced: Decimal
    unit_price: Decimal
    discount_percentage: Decimal
    discount_amount: Decimal
    line_total: Decimal

    tax_code: Optional[str]
    tax_rate: Decimal
    tax_amount: Decimal

    expected_ship_date: Optional[date]
    actual_ship_date: Optional[date]
    attributes: Optional[dict]

    class Config:
        from_attributes = True


class SalesOrderResponse(BaseModel):
    id: UUID
    company_id: UUID
    customer_id: UUID
    order_number: str
    order_date: date
    expected_delivery_date: Optional[date]
    status: str

    subtotal: Decimal
    tax_amount: Decimal
    shipping_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    currency_id: UUID

    shipping_address: Optional[dict]
    shipping_method: Optional[str]
    tracking_number: Optional[str]

    notes: Optional[str]
    internal_notes: Optional[str]

    line_items: List[SalesOrderLineItemResponse]

    class Config:
        from_attributes = True


class SalesOrderUpdate(BaseModel):
    customer_id: Optional[UUID] = None
    expected_delivery_date: Optional[date] = None
    status: Optional[str] = None

    subtotal: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    shipping_amount: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None

    shipping_address: Optional[dict] = None
    shipping_method: Optional[str] = None
    tracking_number: Optional[str] = None

    notes: Optional[str] = None
    internal_notes: Optional[str] = None


class SalesOrderLineItemUpdate(BaseModel):
    sku_id: Optional[UUID] = None
    product_code: Optional[str] = None
    product_name: Optional[str] = None
    description: Optional[str] = None

    quantity_ordered: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    discount_percentage: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    line_total: Optional[Decimal] = None

    tax_code: Optional[str] = None
    tax_rate: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None

    expected_ship_date: Optional[date] = None
    attributes: Optional[dict] = None


class SalesOrderSearchParams(BaseModel):
    customer_id: Optional[UUID] = None
    status: Optional[str] = None
    order_date_from: Optional[date] = None
    order_date_to: Optional[date] = None
    total_amount_min: Optional[Decimal] = None
    total_amount_max: Optional[Decimal] = None


class SalesOrderStatusUpdate(BaseModel):
    status: OrderStatus
    notes: Optional[str] = None


class SalesOrderPaginatedResponse(BaseModel):
    items: List[SalesOrderResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool