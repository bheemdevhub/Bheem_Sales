from typing import List, Optional, Dict, Any, Union, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, desc, asc
import logging
from datetime import datetime, date
from uuid import UUID
import uuid

from bheem_core.modules.sales.core.models.sales_models import (
    SalesOrder, OrderStatus, SalesOrderLineItem, Customer, 
    Quote, QuoteStatus
)
from bheem_core.modules.sales.core.schemas.sales_order_schemas import (
    SalesOrderCreate, SalesOrderUpdate, SalesOrderLineItemCreate, SalesOrderLineItemUpdate,
    SalesOrderSearchParams, SalesOrderStatusUpdate
)
from bheem_core.modules.sales.events.sales_document_events import (
    SalesDocumentEventDispatcher, SalesOrderCreatedEvent, SalesOrderUpdatedEvent, 
    SalesOrderStatusChangedEvent, SalesOrderFulfilledEvent, SalesOrderCancelledEvent, 
    QuoteConvertedToOrderEvent
)
from bheem_core.shared.models import SKU, Activity, ActivityType, ActivityStatus

logger = logging.getLogger(__name__)


class SalesOrderService:
    """
    Service for managing sales order operations
    Handles CRUD operations, search, and business logic for sales orders
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.event_dispatcher = SalesDocumentEventDispatcher()
    
    # Create operations
    
    def create_sales_order(self, order_data: SalesOrderCreate, current_user_id: UUID) -> SalesOrder:
        """Create a new sales order with items"""
        # Generate a unique order number
        order_number = f"SO-{uuid.uuid4().hex[:8].upper()}"
        
        # Create the new SalesOrder object
        new_order = SalesOrder(
            id=uuid.uuid4(),
            order_number=order_number,
            customer_id=order_data.customer_id,
            order_date=order_data.order_date or date.today(),
            expected_delivery_date=order_data.expected_delivery_date,
            subtotal=0.0,  # Will be calculated based on items
            discount_amount=order_data.discount_amount or 0.0,
            discount_percentage=order_data.discount_percentage or 0.0,
            tax_amount=0.0,  # Will be calculated based on items and tax rates
            shipping_amount=order_data.shipping_amount or 0.0,
            total_amount=0.0,  # Will be calculated
            status=OrderStatus.DRAFT,
            currency_id=order_data.currency_id,
            payment_terms=order_data.payment_terms,
            shipping_address=order_data.shipping_address,
            billing_address=order_data.billing_address,
            notes=order_data.notes,
            terms_and_conditions=order_data.terms_and_conditions,
            sales_rep_id=order_data.sales_rep_id,
            company_id=order_data.company_id,
            quote_id=order_data.quote_id,
            created_by=str(current_user_id),
            created_at=datetime.now()
        )
        
        try:
            # Add to database
            self.db.add(new_order)
            self.db.flush()  # Flush to get the ID without committing
            
            # Add order items
            subtotal = 0.0
            tax_amount = 0.0
            
            for item_data in order_data.items:
                # Get SKU information if provided
                sku = None
                if item_data.sku_id:
                    sku = self.db.query(SKU).filter(SKU.id == item_data.sku_id).first()
                
                # Calculate line total
                line_total = item_data.quantity * item_data.unit_price
                if item_data.discount_percentage and item_data.discount_percentage > 0:
                    line_total -= line_total * (item_data.discount_percentage / 100)
                if item_data.discount_amount and item_data.discount_amount > 0:
                    line_total -= item_data.discount_amount
                
                # Calculate tax
                item_tax = 0.0
                if item_data.tax_rate and item_data.tax_rate > 0:
                    item_tax = line_total * (item_data.tax_rate / 100)
                
                # Create order item
                order_item = SalesOrderLineItem(
                    id=uuid.uuid4(),
                    order_id=new_order.id,
                    sku_id=item_data.sku_id,
                    description=item_data.description or (sku.name if sku else ""),
                    quantity=item_data.quantity,
                    unit_price=item_data.unit_price,
                    discount_percentage=item_data.discount_percentage or 0.0,
                    discount_amount=item_data.discount_amount or 0.0,
                    tax_rate=item_data.tax_rate or 0.0,
                    tax_amount=item_tax,
                    line_total=line_total,
                    created_by=str(current_user_id),
                    created_at=datetime.now()
                )
                
                self.db.add(order_item)
                
                # Update totals
                subtotal += line_total
                tax_amount += item_tax
            
            # Update order totals
            new_order.subtotal = subtotal
            new_order.tax_amount = tax_amount
            total = subtotal + tax_amount + new_order.shipping_amount
            
            # Apply order-level discounts
            if new_order.discount_percentage and new_order.discount_percentage > 0:
                discount = subtotal * (new_order.discount_percentage / 100)
                total -= discount
            if new_order.discount_amount and new_order.discount_amount > 0:
                total -= new_order.discount_amount
            
            new_order.total_amount = total
            
            # If created from a quote, update the quote status
            if order_data.quote_id:
                quote = self.db.query(Quote).filter(Quote.id == order_data.quote_id).first()
                if quote and quote.status == QuoteStatus.ACCEPTED:
                    # Mark the quote as converted to order
                    quote.status = QuoteStatus.CONVERTED
                    self.db.flush()
                    
                    # Dispatch quote conversion event
                    self.event_dispatcher.dispatch_event(
                        QuoteConvertedToOrderEvent(
                            quote_id=str(quote.id),
                            order_id=str(new_order.id),
                            customer_id=str(quote.customer_id),
                            company_id=str(quote.company_id),
                            total_amount=float(new_order.total_amount),
                            created_by=str(current_user_id)
                        )
                    )
            
            # Create an activity for the order creation
            activity = Activity(
                id=uuid.uuid4(),
                activity_type=ActivityType.SALES_ORDER_CREATED,
                status=ActivityStatus.COMPLETED,
                subject=f"Sales Order {new_order.order_number} created",
                description=f"Sales order created for customer {new_order.customer_id}",
                related_entity_id=str(new_order.id),
                related_entity_type="sales_order",
                user_id=str(current_user_id),
                company_id=str(new_order.company_id),
                created_by=str(current_user_id),
                created_at=datetime.now()
            )
            self.db.add(activity)
            
            # Commit changes
            self.db.commit()
            
            # Dispatch event
            self.event_dispatcher.dispatch_event(
                SalesOrderCreatedEvent(
                    order_id=str(new_order.id),
                    order_number=new_order.order_number,
                    customer_id=str(new_order.customer_id),
                    company_id=str(new_order.company_id),
                    total_amount=float(new_order.total_amount),
                    created_by=str(current_user_id)
                )
            )
            
            return new_order
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating sales order: {str(e)}")
            raise e
    
    # Read operations
    
    def get_sales_order_by_id(self, order_id: UUID, company_id: UUID) -> Optional[SalesOrder]:
        """Get a sales order by ID"""
        return (
            self.db.query(SalesOrder)
            .filter(SalesOrder.id == order_id, SalesOrder.company_id == company_id)
            .first()
        )
    
    def get_sales_order_by_number(self, order_number: str, company_id: UUID) -> Optional[SalesOrder]:
        """Get a sales order by order number"""
        return (
            self.db.query(SalesOrder)
            .filter(SalesOrder.order_number == order_number, SalesOrder.company_id == company_id)
            .first()
        )
    
    def list_sales_orders(self, search_params: SalesOrderSearchParams) -> Tuple[List[SalesOrder], int]:
        """List sales orders with search and pagination"""
        query = self.db.query(SalesOrder).filter(SalesOrder.company_id == search_params.company_id)
        
        # Apply filters
        if search_params.customer_id:
            query = query.filter(SalesOrder.customer_id == search_params.customer_id)
        
        if search_params.status:
            query = query.filter(SalesOrder.status == search_params.status)
        
        if search_params.start_date:
            query = query.filter(SalesOrder.order_date >= search_params.start_date)
        
        if search_params.end_date:
            query = query.filter(SalesOrder.order_date <= search_params.end_date)
        
        if search_params.min_amount is not None:
            query = query.filter(SalesOrder.total_amount >= search_params.min_amount)
        
        if search_params.max_amount is not None:
            query = query.filter(SalesOrder.total_amount <= search_params.max_amount)
        
        if search_params.query:
            search_term = f"%{search_params.query}%"
            query = query.filter(
                or_(
                    SalesOrder.order_number.ilike(search_term),
                    SalesOrder.notes.ilike(search_term)
                )
            )
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply sorting
        if search_params.sort_by:
            column = getattr(SalesOrder, search_params.sort_by, SalesOrder.created_at)
            if search_params.sort_desc:
                query = query.order_by(desc(column))
            else:
                query = query.order_by(asc(column))
        else:
            # Default sorting by creation date, newest first
            query = query.order_by(desc(SalesOrder.created_at))
        
        # Apply pagination
        if search_params.limit:
            query = query.limit(search_params.limit)
        
        if search_params.offset:
            query = query.offset(search_params.offset)
        
        return query.all(), total_count
    
    # Update operations
    
    def update_sales_order(self, order_id: UUID, order_data: SalesOrderUpdate, current_user_id: UUID) -> SalesOrder:
        """Update an existing sales order"""
        order = self.get_sales_order_by_id(order_id, order_data.company_id)
        if not order:
            raise ValueError(f"Sales order with ID {order_id} not found")
        
        # Check if order is in a state where it can be updated
        if order.status not in [OrderStatus.DRAFT, OrderStatus.CONFIRMED]:
            raise ValueError(f"Sales order with status {order.status} cannot be updated")
        
        # Update basic information
        if order_data.expected_delivery_date:
            order.expected_delivery_date = order_data.expected_delivery_date
        
        if order_data.discount_amount is not None:
            order.discount_amount = order_data.discount_amount
        
        if order_data.discount_percentage is not None:
            order.discount_percentage = order_data.discount_percentage
        
        if order_data.shipping_amount is not None:
            order.shipping_amount = order_data.shipping_amount
        
        if order_data.payment_terms:
            order.payment_terms = order_data.payment_terms
        
        if order_data.shipping_address:
            order.shipping_address = order_data.shipping_address
        
        if order_data.billing_address:
            order.billing_address = order_data.billing_address
        
        if order_data.notes:
            order.notes = order_data.notes
        
        if order_data.terms_and_conditions:
            order.terms_and_conditions = order_data.terms_and_conditions
        
        if order_data.sales_rep_id:
            order.sales_rep_id = order_data.sales_rep_id
        
        # Update last modified information
        order.last_modified_by = str(current_user_id)
        order.last_modified_at = datetime.now()
        
        # Handle items update logic if needed
        # This would typically be implemented separately with item-specific endpoints
        
        # Recalculate totals if needed
        # This might require a separate method that queries items and updates the totals
        
        try:
            self.db.commit()
            
            # Dispatch event
            self.event_dispatcher.dispatch_event(
                SalesOrderUpdatedEvent(
                    order_id=str(order.id),
                    order_number=order.order_number,
                    customer_id=str(order.customer_id),
                    company_id=str(order.company_id),
                    total_amount=float(order.total_amount),
                    updated_by=str(current_user_id)
                )
            )
            
            return order
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating sales order: {str(e)}")
            raise e
    
    def update_sales_order_status(self, order_id: UUID, status_data: SalesOrderStatusUpdate, current_user_id: UUID) -> SalesOrder:
        """Update a sales order's status"""
        order = self.get_sales_order_by_id(order_id, status_data.company_id)
        if not order:
            raise ValueError(f"Sales order with ID {order_id} not found")
        
        old_status = order.status
        new_status = status_data.status
        
        # Validate status transition
        self._validate_status_transition(old_status, new_status)
        
        # Update the status
        order.status = new_status
        order.status_notes = status_data.status_notes
        order.last_modified_by = str(current_user_id)
        order.last_modified_at = datetime.now()
        
        try:
            self.db.commit()
            
            # Create an activity for the status change
            activity = Activity(
                id=uuid.uuid4(),
                activity_type=ActivityType.SALES_ORDER_STATUS_CHANGED,
                status=ActivityStatus.COMPLETED,
                subject=f"Sales Order {order.order_number} status changed",
                description=f"Status changed from {old_status} to {new_status}",
                related_entity_id=str(order.id),
                related_entity_type="sales_order",
                user_id=str(current_user_id),
                company_id=str(order.company_id),
                created_by=str(current_user_id),
                created_at=datetime.now()
            )
            self.db.add(activity)
            self.db.commit()
            
            # Dispatch generic status change event
            self.event_dispatcher.dispatch_event(
                SalesOrderStatusChangedEvent(
                    order_id=str(order.id),
                    order_number=order.order_number,
                    customer_id=str(order.customer_id),
                    company_id=str(order.company_id),
                    old_status=old_status,
                    new_status=new_status,
                    updated_by=str(current_user_id)
                )
            )
            
            # Dispatch specific status events
            if new_status == OrderStatus.CONFIRMED:
                self.event_dispatcher.dispatch_event(
                    SalesOrderFulfilledEvent(
                        order_id=str(order.id),
                        order_number=order.order_number,
                        customer_id=str(order.customer_id),
                        company_id=str(order.company_id),
                        total_amount=float(order.total_amount),
                        updated_by=str(current_user_id)
                    )
                )
            elif new_status == OrderStatus.SHIPPED:
                self.event_dispatcher.dispatch_event(
                    SalesOrderFulfilledEvent(
                        order_id=str(order.id),
                        order_number=order.order_number,
                        customer_id=str(order.customer_id),
                        company_id=str(order.company_id),
                        updated_by=str(current_user_id)
                    )
                )
            elif new_status == OrderStatus.DELIVERED:
                self.event_dispatcher.dispatch_event(
                    SalesOrderFulfilledEvent(
                        order_id=str(order.id),
                        order_number=order.order_number,
                        customer_id=str(order.customer_id),
                        company_id=str(order.company_id),
                        updated_by=str(current_user_id)
                    )
                )
            elif new_status == OrderStatus.CANCELLED:
                self.event_dispatcher.dispatch_event(
                    SalesOrderCancelledEvent(
                        order_id=str(order.id),
                        order_number=order.order_number,
                        customer_id=str(order.customer_id),
                        company_id=str(order.company_id),
                        updated_by=str(current_user_id)
                    )
                )
            
            return order
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating sales order status: {str(e)}")
            raise e
    
    # Helper methods
    
    def _validate_status_transition(self, old_status: OrderStatus, new_status: OrderStatus) -> bool:
        """
        Validate if a status transition is allowed
        Raises ValueError if the transition is invalid
        """
        # Define valid status transitions
        valid_transitions = {
            OrderStatus.DRAFT: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
            OrderStatus.CONFIRMED: [OrderStatus.IN_PROGRESS, OrderStatus.CANCELLED],
            OrderStatus.IN_PROGRESS: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
            OrderStatus.SHIPPED: [OrderStatus.DELIVERED, OrderStatus.RETURNED],
            OrderStatus.DELIVERED: [OrderStatus.RETURNED],
            # CANCELLED and RETURNED are terminal states
        }
        
        # Check if the transition is valid
        if old_status == new_status:
            return True
        
        if old_status not in valid_transitions or new_status not in valid_transitions.get(old_status, []):
            raise ValueError(f"Invalid status transition from {old_status} to {new_status}")
        
        return True
    
    def calculate_sales_order_totals(self, order_id: UUID) -> dict:
        """Recalculate and update sales order totals based on items"""
        order = self.db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
        if not order:
            raise ValueError(f"Sales order with ID {order_id} not found")
        
        # Calculate subtotal and tax from items
        items = self.db.query(SalesOrderLineItem).filter(SalesOrderLineItem.order_id == order_id).all()
        
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
        
        self.db.commit()
        
        return {
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "shipping_amount": order.shipping_amount,
            "discount_amount": order.discount_amount,
            "discount_percentage": order.discount_percentage,
            "total_amount": total
        }

