from typing import List, Optional, Dict, Any, Union, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, desc, asc
import logging
from datetime import datetime, date
from uuid import UUID
import uuid

from bheem_core.modules.sales.core.models.sales_models import (
    SalesInvoice, InvoiceStatus, SalesInvoiceLineItem, Customer,
    SalesOrder, OrderStatus, SalesOrderLineItem
)
from bheem_core.modules.sales.core.schemas.sales_invoice_schemas import (
    SalesInvoiceCreate, SalesInvoiceUpdate, SalesInvoiceLineItemCreate, SalesInvoiceLineItemUpdate,
    SalesInvoiceSearchParams, SalesInvoiceStatusUpdate
)
from bheem_core.modules.sales.events.sales_document_events import (
    SalesDocumentEventDispatcher, SalesInvoiceCreatedEvent, SalesInvoiceUpdatedEvent,
    SalesInvoiceStatusChangedEvent, SalesInvoiceSentEvent, SalesInvoicePaidEvent
)
from bheem_core.shared.models import SKU, Activity, ActivityType, ActivityStatus

logger = logging.getLogger(__name__)


class SalesInvoiceService:
    """
    Service for managing sales invoice operations
    Handles CRUD operations, search, and business logic for sales invoices
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.event_dispatcher = SalesDocumentEventDispatcher()
    
    # Create operations
    
    def create_sales_invoice(self, invoice_data: SalesInvoiceCreate, current_user_id: UUID) -> SalesInvoice:
        """Create a new sales invoice with items"""
        # Generate a unique invoice number
        invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
        
        # Create the new SalesInvoice object
        new_invoice = SalesInvoice(
            id=uuid.uuid4(),
            invoice_number=invoice_number,
            customer_id=invoice_data.customer_id,
            invoice_date=invoice_data.invoice_date or date.today(),
            due_date=invoice_data.due_date,
            subtotal=0.0,  # Will be calculated based on items
            discount_amount=invoice_data.discount_amount or 0.0,
            discount_percentage=invoice_data.discount_percentage or 0.0,
            tax_amount=0.0,  # Will be calculated based on items and tax rates
            shipping_amount=invoice_data.shipping_amount or 0.0,
            total_amount=0.0,  # Will be calculated
            amount_paid=0.0,
            amount_due=0.0,  # Will be calculated
            status=InvoiceStatus.DRAFT,
            currency_id=invoice_data.currency_id,
            payment_terms=invoice_data.payment_terms,
            shipping_address=invoice_data.shipping_address,
            billing_address=invoice_data.billing_address,
            notes=invoice_data.notes,
            terms_and_conditions=invoice_data.terms_and_conditions,
            sales_rep_id=invoice_data.sales_rep_id,
            company_id=invoice_data.company_id,
            order_id=invoice_data.order_id,
            created_by=str(current_user_id),
            created_at=datetime.now()
        )
        
        try:
            # Add to database
            self.db.add(new_invoice)
            self.db.flush()  # Flush to get the ID without committing
            
            # Add invoice items
            subtotal = 0.0
            tax_amount = 0.0
            
            for item_data in invoice_data.items:
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
                
                # Create invoice item
                invoice_item = SalesInvoiceLineItem(
                    id=uuid.uuid4(),
                    invoice_id=new_invoice.id,
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
                
                self.db.add(invoice_item)
                
                # Update totals
                subtotal += line_total
                tax_amount += item_tax
            
            # Update invoice totals
            new_invoice.subtotal = subtotal
            new_invoice.tax_amount = tax_amount
            total = subtotal + tax_amount + new_invoice.shipping_amount
            
            # Apply invoice-level discounts
            if new_invoice.discount_percentage and new_invoice.discount_percentage > 0:
                discount = subtotal * (new_invoice.discount_percentage / 100)
                total -= discount
            if new_invoice.discount_amount and new_invoice.discount_amount > 0:
                total -= new_invoice.discount_amount
            
            new_invoice.total_amount = total
            new_invoice.amount_due = total  # Initially, the full amount is due
            
            # Create an activity for the invoice creation
            activity = Activity(
                id=uuid.uuid4(),
                activity_type=ActivityType.SALES_INVOICE_CREATED,
                status=ActivityStatus.COMPLETED,
                subject=f"Sales Invoice {new_invoice.invoice_number} created",
                description=f"Sales invoice created for customer {new_invoice.customer_id}",
                related_entity_id=str(new_invoice.id),
                related_entity_type="sales_invoice",
                user_id=str(current_user_id),
                company_id=str(new_invoice.company_id),
                created_by=str(current_user_id),
                created_at=datetime.now()
            )
            self.db.add(activity)
            
            # Commit changes
            self.db.commit()
            
            # Dispatch event
            self.event_dispatcher.dispatch_event(
                SalesInvoiceCreatedEvent(
                    invoice_id=str(new_invoice.id),
                    invoice_number=new_invoice.invoice_number,
                    customer_id=str(new_invoice.customer_id),
                    company_id=str(new_invoice.company_id),
                    total_amount=float(new_invoice.total_amount),
                    created_by=str(current_user_id)
                )
            )
            
            return new_invoice
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating sales invoice: {str(e)}")
            raise e
    
    def create_invoice_from_order(self, order_id: UUID, current_user_id: UUID) -> SalesInvoice:
        """Create a new invoice based on an existing sales order"""
        order = self.db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
        if not order:
            raise ValueError(f"Sales order with ID {order_id} not found")
        
        # Check if order is in a valid state for invoice creation
        if order.status not in [OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            raise ValueError(f"Cannot create invoice for order with status {order.status}")
        
        # Get order items
        order_items = self.db.query(SalesOrderLineItem).filter(SalesOrderLineItem.order_id == order_id).all()
        if not order_items:
            raise ValueError(f"Sales order {order_id} has no items")
        
        # Prepare invoice items
        invoice_items = []
        for item in order_items:
            invoice_items.append(
                SalesInvoiceLineItemCreate(
                    sku_id=item.sku_id,
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    discount_percentage=item.discount_percentage,
                    discount_amount=item.discount_amount,
                    tax_rate=item.tax_rate
                )
            )
        
        # Calculate due date based on payment terms (simplified)
        due_date = datetime.now().date()
        if order.payment_terms and "30" in order.payment_terms:
            due_date = due_date.replace(day=due_date.day + 30)
        elif order.payment_terms and "60" in order.payment_terms:
            due_date = due_date.replace(day=due_date.day + 60)
        
        # Create invoice data
        invoice_data = SalesInvoiceCreate(
            customer_id=order.customer_id,
            invoice_date=date.today(),
            due_date=due_date,
            discount_amount=order.discount_amount,
            discount_percentage=order.discount_percentage,
            shipping_amount=order.shipping_amount,
            currency_id=order.currency_id,
            payment_terms=order.payment_terms,
            shipping_address=order.shipping_address,
            billing_address=order.billing_address,
            notes=f"Invoice for sales order {order.order_number}",
            terms_and_conditions=order.terms_and_conditions,
            sales_rep_id=order.sales_rep_id,
            company_id=order.company_id,
            order_id=order.id,
            items=invoice_items
        )
        
        # Create the invoice
        return self.create_sales_invoice(invoice_data, current_user_id)
    
    # Read operations
    
    def get_sales_invoice_by_id(self, invoice_id: UUID, company_id: UUID) -> Optional[SalesInvoice]:
        """Get a sales invoice by ID"""
        return (
            self.db.query(SalesInvoice)
            .filter(SalesInvoice.id == invoice_id, SalesInvoice.company_id == company_id)
            .first()
        )
    
    def get_sales_invoice_by_number(self, invoice_number: str, company_id: UUID) -> Optional[SalesInvoice]:
        """Get a sales invoice by invoice number"""
        return (
            self.db.query(SalesInvoice)
            .filter(SalesInvoice.invoice_number == invoice_number, SalesInvoice.company_id == company_id)
            .first()
        )
    
    def list_sales_invoices(self, search_params: SalesInvoiceSearchParams) -> Tuple[List[SalesInvoice], int]:
        """List sales invoices with search and pagination"""
        query = self.db.query(SalesInvoice).filter(SalesInvoice.company_id == search_params.company_id)
        
        # Apply filters
        if search_params.customer_id:
            query = query.filter(SalesInvoice.customer_id == search_params.customer_id)
        
        if search_params.status:
            query = query.filter(SalesInvoice.status == search_params.status)
        
        if search_params.start_date:
            query = query.filter(SalesInvoice.invoice_date >= search_params.start_date)
        
        if search_params.end_date:
            query = query.filter(SalesInvoice.invoice_date <= search_params.end_date)
        
        if search_params.due_start_date:
            query = query.filter(SalesInvoice.due_date >= search_params.due_start_date)
        
        if search_params.due_end_date:
            query = query.filter(SalesInvoice.due_date <= search_params.due_end_date)
        
        if search_params.min_amount is not None:
            query = query.filter(SalesInvoice.total_amount >= search_params.min_amount)
        
        if search_params.max_amount is not None:
            query = query.filter(SalesInvoice.total_amount <= search_params.max_amount)
        
        if search_params.is_overdue:
            query = query.filter(
                and_(
                    SalesInvoice.due_date < date.today(),
                    SalesInvoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.PARTIAL_PAID])
                )
            )
        
        if search_params.has_payment:
            query = query.filter(SalesInvoice.amount_paid > 0)
        
        if search_params.order_id:
            query = query.filter(SalesInvoice.order_id == search_params.order_id)
        
        if search_params.query:
            search_term = f"%{search_params.query}%"
            query = query.filter(
                or_(
                    SalesInvoice.invoice_number.ilike(search_term),
                    SalesInvoice.notes.ilike(search_term)
                )
            )
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply sorting
        if search_params.sort_by:
            column = getattr(SalesInvoice, search_params.sort_by, SalesInvoice.created_at)
            if search_params.sort_desc:
                query = query.order_by(desc(column))
            else:
                query = query.order_by(asc(column))
        else:
            # Default sorting by invoice date, newest first
            query = query.order_by(desc(SalesInvoice.invoice_date))
        
        # Apply pagination
        if search_params.limit:
            query = query.limit(search_params.limit)
        
        if search_params.offset:
            query = query.offset(search_params.offset)
        
        return query.all(), total_count
    
    # Update operations
    
    def update_sales_invoice(self, invoice_id: UUID, invoice_data: SalesInvoiceUpdate, current_user_id: UUID) -> SalesInvoice:
        """Update an existing sales invoice"""
        invoice = self.get_sales_invoice_by_id(invoice_id, invoice_data.company_id)
        if not invoice:
            raise ValueError(f"Sales invoice with ID {invoice_id} not found")
        
        # Check if invoice is in a state where it can be updated
        if invoice.status not in [InvoiceStatus.DRAFT, InvoiceStatus.SENT]:
            raise ValueError(f"Sales invoice with status {invoice.status} cannot be updated")
        
        # Update basic information
        if invoice_data.due_date:
            invoice.due_date = invoice_data.due_date
        
        if invoice_data.discount_amount is not None:
            invoice.discount_amount = invoice_data.discount_amount
        
        if invoice_data.discount_percentage is not None:
            invoice.discount_percentage = invoice_data.discount_percentage
        
        if invoice_data.shipping_amount is not None:
            invoice.shipping_amount = invoice_data.shipping_amount
        
        if invoice_data.payment_terms:
            invoice.payment_terms = invoice_data.payment_terms
        
        if invoice_data.shipping_address:
            invoice.shipping_address = invoice_data.shipping_address
        
        if invoice_data.billing_address:
            invoice.billing_address = invoice_data.billing_address
        
        if invoice_data.notes:
            invoice.notes = invoice_data.notes
        
        if invoice_data.terms_and_conditions:
            invoice.terms_and_conditions = invoice_data.terms_and_conditions
        
        if invoice_data.sales_rep_id:
            invoice.sales_rep_id = invoice_data.sales_rep_id
        
        # Update last modified information
        invoice.last_modified_by = str(current_user_id)
        invoice.last_modified_at = datetime.now()
        
        # Handle items update logic if needed
        # This would typically be implemented separately with item-specific endpoints
        
        # Recalculate totals if needed
        # This might require a separate method that queries items and updates the totals
        
        try:
            self.db.commit()
            
            # Dispatch event
            self.event_dispatcher.dispatch_event(
                SalesInvoiceUpdatedEvent(
                    invoice_id=str(invoice.id),
                    invoice_number=invoice.invoice_number,
                    customer_id=str(invoice.customer_id),
                    company_id=str(invoice.company_id),
                    total_amount=float(invoice.total_amount),
                    updated_by=str(current_user_id)
                )
            )
            
            return invoice
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating sales invoice: {str(e)}")
            raise e
    
    def update_sales_invoice_status(self, invoice_id: UUID, status_data: SalesInvoiceStatusUpdate, current_user_id: UUID) -> SalesInvoice:
        """Update a sales invoice's status"""
        invoice = self.get_sales_invoice_by_id(invoice_id, status_data.company_id)
        if not invoice:
            raise ValueError(f"Sales invoice with ID {invoice_id} not found")
        
        old_status = invoice.status
        new_status = status_data.status
        
        # Validate status transition
        self._validate_status_transition(old_status, new_status)
        
        # Update the status
        invoice.status = new_status
        invoice.status_notes = status_data.status_notes
        invoice.last_modified_by = str(current_user_id)
        invoice.last_modified_at = datetime.now()
        
        try:
            self.db.commit()
            
            # Create an activity for the status change
            activity = Activity(
                id=uuid.uuid4(),
                activity_type=ActivityType.SALES_INVOICE_STATUS_CHANGED,
                status=ActivityStatus.COMPLETED,
                subject=f"Sales Invoice {invoice.invoice_number} status changed",
                description=f"Status changed from {old_status} to {new_status}",
                related_entity_id=str(invoice.id),
                related_entity_type="sales_invoice",
                user_id=str(current_user_id),
                company_id=str(invoice.company_id),
                created_by=str(current_user_id),
                created_at=datetime.now()
            )
            self.db.add(activity)
            self.db.commit()
            
            # Dispatch generic status change event
            self.event_dispatcher.dispatch_event(
                SalesInvoiceStatusChangedEvent(
                    invoice_id=str(invoice.id),
                    invoice_number=invoice.invoice_number,
                    customer_id=str(invoice.customer_id),
                    company_id=str(invoice.company_id),
                    old_status=old_status,
                    new_status=new_status,
                    updated_by=str(current_user_id)
                )
            )
            
            # Dispatch specific status events
            if new_status == InvoiceStatus.SENT:
                self.event_dispatcher.dispatch_event(
                    SalesInvoiceSentEvent(
                        invoice_id=str(invoice.id),
                        invoice_number=invoice.invoice_number,
                        customer_id=str(invoice.customer_id),
                        company_id=str(invoice.company_id),
                        total_amount=float(invoice.total_amount),
                        updated_by=str(current_user_id)
                    )
                )
            elif new_status == InvoiceStatus.PAID:
                self.event_dispatcher.dispatch_event(
                    SalesInvoicePaidEvent(
                        invoice_id=str(invoice.id),
                        invoice_number=invoice.invoice_number,
                        customer_id=str(invoice.customer_id),
                        company_id=str(invoice.company_id),
                        total_amount=float(invoice.total_amount),
                        updated_by=str(current_user_id)
                    )
                )
            elif new_status == InvoiceStatus.OVERDUE:
                self.event_dispatcher.dispatch_event(
                    SalesInvoiceStatusChangedEvent(
                        invoice_id=str(invoice.id),
                        invoice_number=invoice.invoice_number,
                        customer_id=str(invoice.customer_id),
                        company_id=str(invoice.company_id),
                        total_amount=float(invoice.total_amount),
                        amount_due=float(invoice.amount_due),
                        updated_by=str(current_user_id)
                    )
                )
            elif new_status == InvoiceStatus.CANCELLED:
                self.event_dispatcher.dispatch_event(
                    SalesInvoiceStatusChangedEvent(
                        invoice_id=str(invoice.id),
                        invoice_number=invoice.invoice_number,
                        customer_id=str(invoice.customer_id),
                        company_id=str(invoice.company_id),
                        updated_by=str(current_user_id)
                    )
                )
            
            return invoice
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating sales invoice status: {str(e)}")
            raise e
    
    # Payment operations
    
    def record_payment(self, invoice_id: UUID, amount: float, payment_date: date, payment_method: str, 
                      reference_number: str, notes: str, current_user_id: UUID) -> SalesInvoice:
        """Record a payment against an invoice"""
        invoice = self.db.query(SalesInvoice).filter(SalesInvoice.id == invoice_id).first()
        if not invoice:
            raise ValueError(f"Sales invoice with ID {invoice_id} not found")
        
        # Check if invoice is in a state where payment can be recorded
        if invoice.status not in [InvoiceStatus.SENT, InvoiceStatus.PARTIAL_PAID, InvoiceStatus.OVERDUE]:
            raise ValueError(f"Cannot record payment for invoice with status {invoice.status}")
        
        # Validate payment amount
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero")
        
        if amount > invoice.amount_due:
            raise ValueError(f"Payment amount {amount} exceeds amount due {invoice.amount_due}")
        
        # Update invoice payment information
        old_amount_paid = invoice.amount_paid or 0
        new_amount_paid = old_amount_paid + amount
        new_amount_due = invoice.total_amount - new_amount_paid
        
        invoice.amount_paid = new_amount_paid
        invoice.amount_due = new_amount_due
        invoice.last_payment_date = payment_date
        
        # Update status based on payment
        old_status = invoice.status
        if new_amount_due <= 0:
            invoice.status = InvoiceStatus.PAID
        else:
            invoice.status = InvoiceStatus.PARTIAL_PAID
        
        # Update last modified information
        invoice.last_modified_by = str(current_user_id)
        invoice.last_modified_at = datetime.now()
        
        try:
            self.db.commit()
            
            # Create an activity for the payment
            activity = Activity(
                id=uuid.uuid4(),
                activity_type=ActivityType.PAYMENT_RECORDED,
                status=ActivityStatus.COMPLETED,
                subject=f"Payment recorded for invoice {invoice.invoice_number}",
                description=f"Payment of {amount} recorded via {payment_method}. Reference: {reference_number}",
                related_entity_id=str(invoice.id),
                related_entity_type="sales_invoice",
                user_id=str(current_user_id),
                company_id=str(invoice.company_id),
                created_by=str(current_user_id),
                created_at=datetime.now()
            )
            self.db.add(activity)
            self.db.commit()
            
            # Dispatch status change event if status changed
            if old_status != invoice.status:
                self.event_dispatcher.dispatch_event(
                    SalesInvoiceStatusChangedEvent(
                        invoice_id=str(invoice.id),
                        invoice_number=invoice.invoice_number,
                        customer_id=str(invoice.customer_id),
                        company_id=str(invoice.company_id),
                        old_status=old_status,
                        new_status=invoice.status,
                        updated_by=str(current_user_id)
                    )
                )
                
                if invoice.status == InvoiceStatus.PAID:
                    self.event_dispatcher.dispatch_event(
                        SalesInvoicePaidEvent(
                            invoice_id=str(invoice.id),
                            invoice_number=invoice.invoice_number,
                            customer_id=str(invoice.customer_id),
                            company_id=str(invoice.company_id),
                            total_amount=float(invoice.total_amount),
                            updated_by=str(current_user_id)
                        )
                    )
            
            return invoice
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error recording payment: {str(e)}")
            raise e
    
    # Helper methods
    
    def _validate_status_transition(self, old_status: InvoiceStatus, new_status: InvoiceStatus) -> bool:
        """
        Validate if a status transition is allowed
        Raises ValueError if the transition is invalid
        """
        # Define valid status transitions
        valid_transitions = {
            InvoiceStatus.DRAFT: [InvoiceStatus.SENT, InvoiceStatus.CANCELLED],
            InvoiceStatus.SENT: [InvoiceStatus.PARTIAL_PAID, InvoiceStatus.PAID, InvoiceStatus.OVERDUE, InvoiceStatus.CANCELLED],
            InvoiceStatus.PARTIAL_PAID: [InvoiceStatus.PAID, InvoiceStatus.OVERDUE, InvoiceStatus.CANCELLED],
            InvoiceStatus.OVERDUE: [InvoiceStatus.PARTIAL_PAID, InvoiceStatus.PAID, InvoiceStatus.CANCELLED],
            # PAID, VOID, and CANCELLED are terminal states
        }
        
        # Check if the transition is valid
        if old_status == new_status:
            return True
        
        if old_status not in valid_transitions or new_status not in valid_transitions.get(old_status, []):
            raise ValueError(f"Invalid status transition from {old_status} to {new_status}")
        
        return True
    
    def calculate_sales_invoice_totals(self, invoice_id: UUID) -> dict:
        """Recalculate and update sales invoice totals based on items"""
        invoice = self.db.query(SalesInvoice).filter(SalesInvoice.id == invoice_id).first()
        if not invoice:
            raise ValueError(f"Sales invoice with ID {invoice_id} not found")
        
        # Calculate subtotal and tax from items
        items = self.db.query(SalesInvoiceLineItem).filter(SalesInvoiceLineItem.invoice_id == invoice_id).all()
        
        subtotal = sum(item.line_total for item in items)
        tax_amount = sum(item.tax_amount for item in items)
        
        # Apply invoice-level discounts
        total = subtotal + tax_amount + invoice.shipping_amount
        if invoice.discount_percentage and invoice.discount_percentage > 0:
            discount = subtotal * (invoice.discount_percentage / 100)
            total -= discount
        if invoice.discount_amount and invoice.discount_amount > 0:
            total -= invoice.discount_amount
        
        # Update invoice
        invoice.subtotal = subtotal
        invoice.tax_amount = tax_amount
        invoice.total_amount = total
        invoice.amount_due = total - (invoice.amount_paid or 0)
        
        self.db.commit()
        
        return {
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "shipping_amount": invoice.shipping_amount,
            "discount_amount": invoice.discount_amount,
            "discount_percentage": invoice.discount_percentage,
            "total_amount": total,
            "amount_paid": invoice.amount_paid,
            "amount_due": invoice.amount_due
        }
    
    def check_overdue_invoices(self, company_id: UUID) -> List[SalesInvoice]:
        """Check for invoices that are past due date and update status"""
        today = date.today()
        
        # Find invoices that are past due date but not marked as overdue
        overdue_invoices = (
            self.db.query(SalesInvoice)
            .filter(
                SalesInvoice.company_id == company_id,
                SalesInvoice.due_date < today,
                SalesInvoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.PARTIAL_PAID]),
                SalesInvoice.amount_due > 0
            )
            .all()
        )
        
        # Update invoice status to overdue
        for invoice in overdue_invoices:
            old_status = invoice.status
            invoice.status = InvoiceStatus.OVERDUE
            invoice.last_modified_at = datetime.now()
            
            # Dispatch overdue event
            self.event_dispatcher.dispatch_event(
                SalesInvoiceStatusChangedEvent(
                    invoice_id=str(invoice.id),
                    invoice_number=invoice.invoice_number,
                    customer_id=str(invoice.customer_id),
                    company_id=str(invoice.company_id),
                    total_amount=float(invoice.total_amount),
                    amount_due=float(invoice.amount_due),
                    updated_by="system"
                )
            )
            
            # Also dispatch status change event
            self.event_dispatcher.dispatch_event(
                SalesInvoiceStatusChangedEvent(
                    invoice_id=str(invoice.id),
                    invoice_number=invoice.invoice_number,
                    customer_id=str(invoice.customer_id),
                    company_id=str(invoice.company_id),
                    old_status=old_status,
                    new_status=InvoiceStatus.OVERDUE,
                    updated_by="system"
                )
            )
        
        if overdue_invoices:
            self.db.commit()
        
        return overdue_invoices

