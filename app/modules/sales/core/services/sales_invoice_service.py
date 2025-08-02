import traceback
from typing import List, Optional, Dict, Any, Union, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, or_, and_, desc, asc, select
import logging
from datetime import datetime, date
from uuid import UUID, uuid4
import uuid
from fastapi import HTTPException

from app.modules.sales.core.models.sales_models import (
    SalesInvoice, InvoiceStatus, SalesInvoiceLineItem, Customer,
    SalesOrder, OrderStatus, SalesOrderLineItem
)
from app.modules.sales.core.schemas.sales_invoice_schemas import (
    SalesInvoiceCreate, SalesInvoiceUpdate, SalesInvoiceLineItemCreate, SalesInvoiceLineItemUpdate,
    SalesInvoiceSearchParams, SalesInvoiceStatusUpdate, SalesInvoiceResponse
)
from app.modules.sales.events.sales_document_events import (
    SalesDocumentEventDispatcher, SalesInvoiceCreatedEvent, SalesInvoiceUpdatedEvent,
    SalesInvoiceStatusChangedEvent, SalesInvoiceSentEvent, SalesInvoicePaidEvent
)
from app.shared.models import SKU, Activity, ActivityType, ActivityStatus

logger = logging.getLogger(__name__)


class SalesInvoiceService:
    """
    Service for managing sales invoice operations
    Handles CRUD operations, search, and business logic for sales invoices
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db  # Injected AsyncSession
    
    # Create operations
    
    async def create_invoice(self, invoice_data: SalesInvoiceCreate, current_user_id: UUID, company_id: UUID):
        try:
            # Check if order number already exists (optional business logic)
            if invoice_data.invoice_number:
                existing = await self.db.execute(
                    select(SalesInvoice).where(
                        SalesInvoice.company_id == company_id,
                        SalesInvoice.invoice_number == invoice_data.invoice_number
                    )
                )
                if existing.scalar_one_or_none():
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invoice number '{invoice_data.invoice_number}' already exists for this company."
                    )

            # Validate SKUs
            for item in invoice_data.line_items:
                sku = await self.db.get(SKU, item.sku_id)
                if not sku:
                    raise HTTPException(status_code=404, detail=f"SKU not found: {item.sku_id}")

            # Create invoice
            invoice = SalesInvoice(
                id=uuid4(),
                company_id=company_id,
                customer_id=invoice_data.customer_id,
                sales_order_id=invoice_data.sales_order_id,
                invoice_number=invoice_data.invoice_number,
                invoice_date=invoice_data.invoice_date,
                due_date=invoice_data.due_date,
                status=invoice_data.status,
                subtotal=invoice_data.subtotal,
                tax_amount=invoice_data.tax_amount,
                discount_amount=invoice_data.discount_amount,
                total_amount=invoice_data.total_amount,
                paid_amount=invoice_data.paid_amount,
                balance_due=invoice_data.balance_due,
                currency_id=invoice_data.currency_id,
                payment_terms=invoice_data.payment_terms,
                late_fee_rate=invoice_data.late_fee_rate,
                notes=invoice_data.notes,
                created_by=current_user_id,
                updated_by=current_user_id
            )
            self.db.add(invoice)
            await self.db.flush()  # ✅ Flush to get invoice.id

            # Create invoice line items
            for index, item in enumerate(invoice_data.line_items, start=1):
                line_item = SalesInvoiceLineItem(
                    id=uuid4(),
                    sales_invoice_id=invoice.id,  # ✅ Use flushed ID
                    line_number=index,
                    sku_id=item.sku_id,
                    product_code=item.product_code,
                    product_name=item.product_name,
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    discount_percentage=item.discount_percentage,
                    discount_amount=item.discount_amount,
                    line_total=item.line_total,
                    tax_code=item.tax_code,
                    tax_rate=item.tax_rate,
                    tax_amount=item.tax_amount,
                    attributes=item.attributes
                )
                self.db.add(line_item)

            await self.db.commit()
            await self.db.refresh(invoice, attribute_names=["line_items"])
            return SalesInvoiceResponse.model_validate(invoice, from_attributes=True)

        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create invoice: {str(e)}")
        
    
    # Update operations
    
    async def update_sales_invoice(self, invoice_id: UUID, invoice_data: SalesInvoiceUpdate, current_user_id: UUID) -> SalesInvoice:
        """Update an existing sales invoice"""
        invoice = await self.get_sales_invoice_by_id(invoice_id, invoice_data.company_id)
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
            await self.db.commit()
            
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
            await self.db.rollback()
            logger.error(f"Error updating sales invoice: {str(e)}")
            raise e
    
    async def update_sales_invoice_status(self, invoice_id: UUID, status_data: SalesInvoiceStatusUpdate, current_user_id: UUID) -> SalesInvoice:
        """Update a sales invoice's status"""
        invoice = await self.get_sales_invoice_by_id(invoice_id, status_data.company_id)
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
            await self.db.commit()
            
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
    
    async def record_payment(self, invoice_id: UUID, amount: float, payment_date: date, payment_method: str, 
                      reference_number: str, notes: str, current_user_id: UUID) -> SalesInvoice:
        """Record a payment against an invoice"""
        result = await self.db.execute(select(SalesInvoice).where(SalesInvoice.id == invoice_id))
        invoice = result.scalar_one_or_none()
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
            await self.db.commit()
            
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
            await self.db.commit()
            
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
            await self.db.rollback()
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
    
    async def calculate_sales_invoice_totals(self, invoice_id: UUID) -> dict:
        """Recalculate and update sales invoice totals based on items"""
        result = await self.db.execute(select(SalesInvoice).where(SalesInvoice.id == invoice_id))
        invoice = result.scalar_one_or_none()
        if not invoice:
            raise ValueError(f"Sales invoice with ID {invoice_id} not found")
        
        # Calculate subtotal and tax from items
        items_result = await self.db.execute(select(SalesInvoiceLineItem).where(SalesInvoiceLineItem.invoice_id == invoice_id))
        items = items_result.scalars().all()
        
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
        
        await self.db.commit()
        
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
    
    async def check_overdue_invoices(self, company_id: UUID) -> List[SalesInvoice]:
        """Check for invoices that are past due date and update status"""
        today = date.today()
        
        # Find invoices that are past due date but not marked as overdue
        result = await self.db.execute(
            select(SalesInvoice)
            .where(
                SalesInvoice.company_id == company_id,
                SalesInvoice.due_date < today,
                SalesInvoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.PARTIAL_PAID]),
                SalesInvoice.amount_due > 0
            )
        )
        overdue_invoices = result.scalars().all()
        
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
            await self.db.commit()
        
        return overdue_invoices
