from typing import List, Optional, Dict, Any, Union, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import func, or_, and_, desc, asc, select
import logging
from datetime import datetime, date
from fastapi import HTTPException
from uuid import UUID, uuid4
import uuid

from app.modules.sales.core.models.sales_models import (
    SalesOrder, OrderStatus, SalesOrderLineItem, Customer, 
    Quote, QuoteStatus
)
from app.modules.sales.core.schemas.sales_order_schemas import (
    SalesOrderCreate, SalesOrderUpdate, SalesOrderLineItemCreate, SalesOrderLineItemUpdate,
    SalesOrderSearchParams, SalesOrderStatusUpdate, SalesOrderResponse
)
from app.modules.sales.events.sales_document_events import (
    SalesDocumentEventDispatcher, SalesOrderCreatedEvent, SalesOrderUpdatedEvent, 
    SalesOrderStatusChangedEvent, SalesOrderFulfilledEvent, SalesOrderCancelledEvent, 
    QuoteConvertedToOrderEvent
)
from app.shared.models import SKU, Activity, ActivityType, ActivityStatus

logger = logging.getLogger(__name__)


class SalesOrderService:
    """
    Service for managing sales order operations
    Handles CRUD operations, search, and business logic for sales orders
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.event_dispatcher = SalesDocumentEventDispatcher()
    
    # Create operations
    
    
    async def create_sales_order(self, order_data: SalesOrderCreate, current_user_id: UUID, company_id: UUID):
        try:
            # Step 1: Check if order number already exists for the company
            existing = await self.db.execute(
                select(SalesOrder).where(
                    SalesOrder.company_id == company_id,
                    SalesOrder.order_number == order_data.order_number
                )
            )
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=400,
                    detail=f"Order number '{order_data.order_number}' already exists for this company."
                )

            # Step 2: Create Sales Order
            new_order = SalesOrder(
                id=uuid4(),
                company_id=company_id,
                customer_id=order_data.customer_id,
                quote_id=order_data.quote_id,
                order_number=order_data.order_number,
                order_date=order_data.order_date,
                expected_delivery_date=order_data.expected_delivery_date,
                status=order_data.status,
                subtotal=order_data.subtotal,
                tax_amount=order_data.tax_amount,
                shipping_amount=order_data.shipping_amount,
                discount_amount=order_data.discount_amount,
                total_amount=order_data.total_amount,
                currency_id=order_data.currency_id,
                shipping_address=order_data.shipping_address,
                shipping_method=order_data.shipping_method,
                tracking_number=order_data.tracking_number,
                notes=order_data.notes,
                internal_notes=order_data.internal_notes,
                created_by=current_user_id,
                updated_by=current_user_id
            )
            self.db.add(new_order)

            # Step 3: Add line items
            for index, item in enumerate(order_data.line_items, start=1):
                sku = await self.db.get(SKU, item.sku_id)
                if not sku:
                    raise HTTPException(status_code=404, detail=f"SKU not found: {item.sku_id}")

                line_item = SalesOrderLineItem(
                    id=uuid4(),
                    sales_order=new_order,
                    line_number=index,
                    sku_id=item.sku_id,
                    product_code=item.product_code,
                    product_name=item.product_name,
                    description=item.description,
                    quantity_ordered=item.quantity_ordered,
                    quantity_shipped=0,
                    quantity_invoiced=0,
                    unit_price=item.unit_price,
                    discount_percentage=item.discount_percentage,
                    discount_amount=item.discount_amount,
                    line_total=item.line_total,
                    tax_code=item.tax_code,
                    tax_rate=item.tax_rate,
                    tax_amount=item.tax_amount,
                    expected_ship_date=item.expected_ship_date,
                    attributes=item.attributes
                )
                self.db.add(line_item)

            # Step 4: Commit and refresh with line_items
            await self.db.commit()
            await self.db.refresh(new_order, attribute_names=["line_items"])

            # Step 5: Return validated Pydantic response
            return SalesOrderResponse.model_validate(new_order, from_attributes=True)

        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create sales order: {str(e)}")

        
    
    
    async def calculate_sales_order_totals(self, order_id: UUID) -> dict:
        """Recalculate and update sales order totals based on items"""
        order = await self.db.get(SalesOrder, order_id)
        if not order:
            raise ValueError(f"Sales order with ID {order_id} not found")
        
        # Calculate subtotal and tax from items
        stmt = select(SalesOrderLineItem).where(SalesOrderLineItem.sales_order_id == order_id)
        result = await self.db.execute(stmt)
        items = result.scalars().all()
        
        subtotal = sum(item.line_total for item in items)
        tax_amount = sum(item.tax_amount for item in items)
        
        # Apply order-level discounts
        total = subtotal + tax_amount + order.shipping_amount
        if order.discount_percentage and order.discount_percentage > 0:
            discount = subtotal * (order.discount_percentage / 100)
            total -= discount
        if order.discount_amount and order.discount_amount > 0:
            total -= order.discount_amount
        
        # Update order
        order.subtotal = subtotal
        order.tax_amount = tax_amount
        order.total_amount = total
        
        await self.db.commit()
        
        return {
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "shipping_amount": order.shipping_amount,
            "discount_amount": order.discount_amount,
            "discount_percentage": order.discount_percentage,
            "total_amount": total
        }

    async def get_sales_order_by_id(self, order_id: UUID, company_id: UUID) -> Optional[SalesOrder]:
        """Get a sales order by ID"""
        stmt = select(SalesOrder).options(
            selectinload(SalesOrder.line_items),
            selectinload(SalesOrder.customer)
        ).where(
            SalesOrder.id == order_id,
            SalesOrder.company_id == company_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_sales_orders(
        self, 
        company_id: UUID, 
        skip: int = 0, 
        limit: int = 100,
        search_params: Optional[SalesOrderSearchParams] = None
    ) -> Tuple[List[SalesOrder], int]:
        """List sales orders with pagination and filtering"""
        query = select(SalesOrder).where(SalesOrder.company_id == company_id)
        
        if search_params:
            if search_params.customer_id:
                query = query.where(SalesOrder.customer_id == search_params.customer_id)
            if search_params.status:
                query = query.where(SalesOrder.status == search_params.status)
            if search_params.order_date_from:
                query = query.where(SalesOrder.order_date >= search_params.order_date_from)
            if search_params.order_date_to:
                query = query.where(SalesOrder.order_date <= search_params.order_date_to)
            if search_params.total_amount_min:
                query = query.where(SalesOrder.total_amount >= search_params.total_amount_min)
            if search_params.total_amount_max:
                query = query.where(SalesOrder.total_amount <= search_params.total_amount_max)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.options(
            selectinload(SalesOrder.line_items),
            selectinload(SalesOrder.customer)
        ).offset(skip).limit(limit).order_by(desc(SalesOrder.created_at))
        
        result = await self.db.execute(query)
        orders = result.scalars().all()
        
        return orders, total

    async def update_sales_order(
        self, 
        order_id: UUID, 
        company_id: UUID, 
        order_data: SalesOrderUpdate, 
        current_user_id: UUID
    ) -> Optional[SalesOrder]:
        """Update a sales order"""
        order = await self.db.get(SalesOrder, order_id)
        if not order or order.company_id != company_id:
            return None
        
        # Update fields
        for field, value in order_data.dict(exclude_unset=True).items():
            setattr(order, field, value)
        
        order.updated_by = current_user_id
        order.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def update_sales_order_status(
        self, 
        order_id: UUID, 
        company_id: UUID, 
        status_data: SalesOrderStatusUpdate, 
        current_user_id: UUID
    ) -> Optional[SalesOrder]:
        """Update sales order status"""
        order = await self.db.get(SalesOrder, order_id)
        if not order or order.company_id != company_id:
            return None
        
        old_status = order.status
        order.status = status_data.status
        if status_data.notes:
            order.internal_notes = f"{order.internal_notes or ''}\n{status_data.notes}".strip()
        
        order.updated_by = current_user_id
        order.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        # Dispatch status change event
        event = SalesOrderStatusChangedEvent(
            order_id=order.id,
            old_status=old_status,
            new_status=order.status,
            user_id=current_user_id,
            company_id=company_id
        )
        await self.event_dispatcher.dispatch(event)
        
        await self.db.refresh(order)
        return order
