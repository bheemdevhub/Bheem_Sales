from typing import List, Optional, Dict, Any, Union, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, or_, and_, desc, asc, select
import logging
from datetime import datetime, date
from uuid import UUID
import uuid

from app.modules.sales.core.models.sales_models import Quote, QuoteStatus, QuoteLineItem, Customer
from app.modules.sales.core.schemas.quote_schemas import (
    QuoteCreate, QuoteUpdate, QuoteLineItemCreate, QuoteLineItemUpdate,
    QuoteSearchParams, QuoteStatusUpdate
)
from app.modules.sales.events.sales_document_events import (
    SalesDocumentEventDispatcher, QuoteCreatedEvent, QuoteUpdatedEvent, 
    QuoteStatusChangedEvent, QuoteSentEvent, QuoteAcceptedEvent, 
    QuoteRejectedEvent, QuoteConvertedToOrderEvent
)
from app.shared.models import SKU, Activity, ActivityType, ActivityStatus

logger = logging.getLogger(__name__)


class QuoteService:
    """
    Service for managing quote-related operations
    Handles CRUD operations, search, and business logic for quotes
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.event_dispatcher = SalesDocumentEventDispatcher()
    
    # Create operations
    
    async def create_quote(self, quote_data: QuoteCreate, current_user_id: UUID) -> Quote:
        """Create a new quote with items"""
        # Generate a unique quote number (in real implementation, this would use a sequence)
        quote_number = f"QT-{uuid.uuid4().hex[:8].upper()}"
        
        # Create the new Quote object
        new_quote = Quote(
            id=uuid.uuid4(),
            quote_number=quote_number,
            customer_id=quote_data.customer_id,
            quote_date=quote_data.quote_date or date.today(),
            expiry_date=quote_data.expiry_date,
            subtotal=0.0,  # Will be calculated based on items
            discount_amount=quote_data.discount_amount or 0.0,
            discount_percentage=quote_data.discount_percentage or 0.0,
            tax_amount=0.0,  # Will be calculated based on items and tax rates
            total_amount=0.0,  # Will be calculated
            status=QuoteStatus.DRAFT,
            currency_id=quote_data.currency_id,
            payment_terms=quote_data.payment_terms,
            shipping_address=quote_data.shipping_address,
            billing_address=quote_data.billing_address,
            notes=quote_data.notes,
            terms_and_conditions=quote_data.terms_and_conditions,
            sales_rep_id=quote_data.sales_rep_id,
            company_id=quote_data.company_id,
            created_by=str(current_user_id),
            created_at=datetime.now()
        )
        
        try:
            # Add to database
            self.db.add(new_quote)
            self.db.flush()  # Flush to get the ID without committing
            
            # Add quote items
            subtotal = 0.0
            tax_amount = 0.0
            
            for item_data in quote_data.items:
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
                
                # Create quote item
                quote_item = QuoteLineItem(
                    id=uuid.uuid4(),
                    quote_id=new_quote.id,
                    sku_id=item_data.sku_id,
                    description=item_data.description or (sku.name if sku else ""),
                    quantity=item_data.quantity,
                    unit_price=item_data.unit_price,
                    discount_percentage=item_data.discount_percentage or 0.0,
                    discount_amount=item_data.discount_amount or 0.0,
                    tax_rate=item_data.tax_rate or 0.0,
                    tax_amount=item_tax,
                    line_total=line_total,
                    sort_order=item_data.sort_order or 0
                )
                
                self.db.add(quote_item)
                
                # Update running totals
                subtotal += line_total
                tax_amount += item_tax
            
            # Update quote totals
            new_quote.subtotal = subtotal
            
            # Apply quote-level discount
            discount = 0.0
            if new_quote.discount_percentage and new_quote.discount_percentage > 0:
                discount = subtotal * (new_quote.discount_percentage / 100)
            if new_quote.discount_amount and new_quote.discount_amount > 0:
                discount += new_quote.discount_amount
            
            new_quote.tax_amount = tax_amount
            new_quote.total_amount = subtotal - discount + tax_amount
            
            # Get customer name for event
            customer = self.db.query(Customer).filter(Customer.id == quote_data.customer_id).first()
            customer_name = customer.display_name if customer else "Unknown Customer"
            
            # Dispatch event
            self.event_dispatcher.dispatch(
                QuoteCreatedEvent(
                    quote_id=new_quote.id,
                    quote_number=new_quote.quote_number,
                    customer_id=new_quote.customer_id,
                    customer_name=customer_name,
                    total_amount=float(new_quote.total_amount),
                    company_id=new_quote.company_id,
                    user_id=current_user_id
                )
            )
            
            # Commit changes
            self.db.commit()
            self.db.refresh(new_quote)
            
            return new_quote
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating quote: {str(e)}")
            raise
    
    # Read operations
    
    async def get_quote_by_id(self, quote_id: UUID, company_id: UUID) -> Optional[Quote]:
        """Get a quote by ID and company ID"""
        return self.db.query(Quote).filter(
            and_(
                Quote.id == quote_id,
                Quote.company_id == company_id
            )
        ).first()
    
    async def get_quote_by_number(self, quote_number: str, company_id: UUID) -> Optional[Quote]:
        """Get a quote by number and company ID"""
        return self.db.query(Quote).filter(
            and_(
                Quote.quote_number == quote_number,
                Quote.company_id == company_id
            )
        ).first()
    
    async def list_quotes(self, 
                   company_id: UUID,
                   search_params: QuoteSearchParams = None,
                   skip: int = 0, 
                   limit: int = 100) -> Tuple[List[Quote], int]:
        """
        List quotes with optional filtering and pagination
        Returns tuple of (quotes, total_count)
        """
        query = self.db.query(Quote).filter(Quote.company_id == company_id)
        
        # Apply filters if search_params is provided
        if search_params:
            if search_params.query:
                search_term = f"%{search_params.query}%"
                query = query.filter(
                    or_(
                        Quote.quote_number.ilike(search_term),
                        Quote.notes.ilike(search_term)
                    )
                )
            
            if search_params.customer_id:
                query = query.filter(Quote.customer_id == search_params.customer_id)
            
            if search_params.status:
                query = query.filter(Quote.status == search_params.status)
            
            if search_params.sales_rep_id:
                query = query.filter(Quote.sales_rep_id == str(search_params.sales_rep_id))
            
            if search_params.created_after:
                query = query.filter(Quote.created_at >= search_params.created_after)
            
            if search_params.created_before:
                query = query.filter(Quote.created_at <= search_params.created_before)
            
            if search_params.quote_date_after:
                query = query.filter(Quote.quote_date >= search_params.quote_date_after)
            
            if search_params.quote_date_before:
                query = query.filter(Quote.quote_date <= search_params.quote_date_before)
            
            if search_params.expiry_date_after:
                query = query.filter(Quote.expiry_date >= search_params.expiry_date_after)
            
            if search_params.expiry_date_before:
                query = query.filter(Quote.expiry_date <= search_params.expiry_date_before)
            
            if search_params.min_total is not None:
                query = query.filter(Quote.total_amount >= search_params.min_total)
            
            if search_params.max_total is not None:
                query = query.filter(Quote.total_amount <= search_params.max_total)
            
            # Handle sorting
            if search_params.sort_by:
                sort_column = getattr(Quote, search_params.sort_by, Quote.quote_date)
                if search_params.sort_desc:
                    sort_column = desc(sort_column)
                else:
                    sort_column = asc(sort_column)
                query = query.order_by(sort_column)
            else:
                # Default sorting
                query = query.order_by(desc(Quote.quote_date))
        else:
            # Default sorting if no search_params
            query = query.order_by(desc(Quote.quote_date))
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        return query.all(), total_count
    
    async def get_quote_items(self, quote_id: UUID) -> List[QuoteLineItem]:
        """Get all items for a quote"""
        return self.db.query(QuoteLineItem).filter(QuoteLineItem.quote_id == quote_id).order_by(QuoteLineItem.sort_order).all()
    
    # Update operations
    
    async def update_quote(self, 
                    quote_id: UUID, 
                    company_id: UUID,
                    quote_data: QuoteUpdate, 
                    current_user_id: UUID) -> Optional[Quote]:
        """Update an existing quote"""
        quote = self.get_quote_by_id(quote_id, company_id)
        
        if not quote:
            return None
        
        # Check if status is changing to dispatch proper event
        status_changing = quote_data.status is not None and quote.status != quote_data.status
        old_status = quote.status.value if status_changing else None
        
        # Update fields from the provided data
        for key, value in quote_data.dict(exclude_unset=True, exclude={"items"}).items():
            setattr(quote, key, value)
        
        # Always update the updated_at and updated_by fields
        quote.updated_at = datetime.now()
        quote.updated_by = str(current_user_id)
        
        try:
            # Handle quote items if provided
            if quote_data.items is not None:
                # Remove existing items that are not in the updated list
                existing_items = self.get_quote_items(quote_id)
                existing_item_ids = {str(item.id) for item in existing_items}
                updated_item_ids = {str(item.id) for item in quote_data.items if item.id is not None}
                
                # Delete items that are not in the updated list
                for item_id in existing_item_ids - updated_item_ids:
                    item_to_delete = next((item for item in existing_items if str(item.id) == item_id), None)
                    if item_to_delete:
                        self.db.delete(item_to_delete)
                
                # Update or add items
                subtotal = 0.0
                tax_amount = 0.0
                
                for item_data in quote_data.items:
                    if item_data.id is not None:
                        # Update existing item
                        item = next((item for item in existing_items if str(item.id) == str(item_data.id)), None)
                        if item:
                            # Get SKU information if provided and changed
                            sku = None
                            if item_data.sku_id and item_data.sku_id != item.sku_id:
                                sku = self.db.query(SKU).filter(SKU.id == item_data.sku_id).first()
                            
                            # Update item fields
                            for key, value in item_data.dict(exclude_unset=True).items():
                                setattr(item, key, value)
                            
                            # Calculate line total
                            line_total = item.quantity * item.unit_price
                            if item.discount_percentage and item.discount_percentage > 0:
                                line_total -= line_total * (item.discount_percentage / 100)
                            if item.discount_amount and item.discount_amount > 0:
                                line_total -= item.discount_amount
                            
                            # Calculate tax
                            item_tax = 0.0
                            if item.tax_rate and item.tax_rate > 0:
                                item_tax = line_total * (item.tax_rate / 100)
                            
                            item.tax_amount = item_tax
                            item.line_total = line_total
                            
                            # Update running totals
                            subtotal += line_total
                            tax_amount += item_tax
                    else:
                        # Add new item
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
                        
                        # Create quote item
                        quote_item = QuoteLineItem(
                            id=uuid.uuid4(),
                            quote_id=quote.id,
                            sku_id=item_data.sku_id,
                            description=item_data.description or (sku.name if sku else ""),
                            quantity=item_data.quantity,
                            unit_price=item_data.unit_price,
                            discount_percentage=item_data.discount_percentage or 0.0,
                            discount_amount=item_data.discount_amount or 0.0,
                            tax_rate=item_data.tax_rate or 0.0,
                            tax_amount=item_tax,
                            line_total=line_total,
                            sort_order=item_data.sort_order or 0
                        )
                        
                        self.db.add(quote_item)
                        
                        # Update running totals
                        subtotal += line_total
                        tax_amount += item_tax
                
                # Update quote totals
                quote.subtotal = subtotal
                
                # Apply quote-level discount
                discount = 0.0
                if quote.discount_percentage and quote.discount_percentage > 0:
                    discount = subtotal * (quote.discount_percentage / 100)
                if quote.discount_amount and quote.discount_amount > 0:
                    discount += quote.discount_amount
                
                quote.tax_amount = tax_amount
                quote.total_amount = subtotal - discount + tax_amount
            
            # Get customer name for event
            customer = self.db.query(Customer).filter(Customer.id == quote.customer_id).first()
            customer_name = customer.display_name if customer else "Unknown Customer"
            
            # Dispatch generic update event
            self.event_dispatcher.dispatch(
                QuoteUpdatedEvent(
                    quote_id=quote.id,
                    quote_number=quote.quote_number,
                    customer_id=quote.customer_id,
                    customer_name=customer_name,
                    total_amount=float(quote.total_amount),
                    company_id=quote.company_id,
                    user_id=current_user_id
                )
            )
            
            # Dispatch status change event if applicable
            if status_changing:
                self.event_dispatcher.dispatch(
                    QuoteStatusChangedEvent(
                        quote_id=quote.id,
                        quote_number=quote.quote_number,
                        customer_id=quote.customer_id,
                        customer_name=customer_name,
                        old_status=old_status,
                        new_status=quote.status.value,
                        company_id=quote.company_id,
                        user_id=current_user_id
                    )
                )
            
            # Commit changes
            self.db.commit()
            self.db.refresh(quote)
            
            return quote
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating quote: {str(e)}")
            raise
    
    async def update_quote_status(self, 
                           quote_id: UUID, 
                           company_id: UUID,
                           status_data: QuoteStatusUpdate, 
                           current_user_id: UUID) -> Optional[Quote]:
        """Update a quote's status"""
        quote = self.get_quote_by_id(quote_id, company_id)
        
        if not quote:
            return None
        
        old_status = quote.status.value
        
        # Only update if status is actually changing
        if quote.status != status_data.status:
            quote.status = status_data.status
            
            # Additional fields based on status
            if status_data.status == QuoteStatus.SENT:
                quote.sent_date = datetime.now()
                quote.sent_by = str(current_user_id)
                quote.sent_to = status_data.sent_to
            elif status_data.status == QuoteStatus.ACCEPTED:
                quote.accepted_date = datetime.now()
                quote.accepted_by = str(current_user_id)
            elif status_data.status == QuoteStatus.REJECTED:
                quote.rejection_reason = status_data.reason
            
            quote.updated_at = datetime.now()
            quote.updated_by = str(current_user_id)
            
            try:
                # Get customer name for event
                customer = self.db.query(Customer).filter(Customer.id == quote.customer_id).first()
                customer_name = customer.display_name if customer else "Unknown Customer"
                
                # Dispatch status change event
                self.event_dispatcher.dispatch(
                    QuoteStatusChangedEvent(
                        quote_id=quote.id,
                        quote_number=quote.quote_number,
                        customer_id=quote.customer_id,
                        customer_name=customer_name,
                        old_status=old_status,
                        new_status=quote.status.value,
                        company_id=quote.company_id,
                        user_id=current_user_id
                    )
                )
                
                # Dispatch additional status-specific events
                if status_data.status == QuoteStatus.SENT:
                    self.event_dispatcher.dispatch(
                        QuoteSentEvent(
                            quote_id=quote.id,
                            quote_number=quote.quote_number,
                            customer_id=quote.customer_id,
                            customer_name=customer_name,
                            sent_to=quote.sent_to,
                            total_amount=float(quote.total_amount),
                            company_id=quote.company_id,
                            user_id=current_user_id
                        )
                    )
                elif status_data.status == QuoteStatus.ACCEPTED:
                    self.event_dispatcher.dispatch(
                        QuoteAcceptedEvent(
                            quote_id=quote.id,
                            quote_number=quote.quote_number,
                            customer_id=quote.customer_id,
                            customer_name=customer_name,
                            total_amount=float(quote.total_amount),
                            company_id=quote.company_id,
                            user_id=current_user_id
                        )
                    )
                elif status_data.status == QuoteStatus.REJECTED:
                    self.event_dispatcher.dispatch(
                        QuoteRejectedEvent(
                            quote_id=quote.id,
                            quote_number=quote.quote_number,
                            customer_id=quote.customer_id,
                            customer_name=customer_name,
                            reason=quote.rejection_reason,
                            company_id=quote.company_id,
                            user_id=current_user_id
                        )
                    )
                
                # Commit changes
                self.db.commit()
                self.db.refresh(quote)
                
            except Exception as e:
                self.db.rollback()
                logger.error(f"Error updating quote status: {str(e)}")
                raise
        
        return quote
    
    # Additional business operations
    
    async def convert_quote_to_order(self, 
                              quote_id: UUID, 
                              company_id: UUID,
                              current_user_id: UUID) -> Dict[str, Any]:
        """Convert a quote to a sales order"""
        quote = self.get_quote_by_id(quote_id, company_id)
        
        if not quote:
            return {"success": False, "message": "Quote not found"}
        
        # Check if quote can be converted
        if quote.status not in [QuoteStatus.ACCEPTED, QuoteStatus.SENT]:
            return {
                "success": False, 
                "message": f"Quote must be in ACCEPTED or SENT status to convert to order. Current status: {quote.status.value}"
            }
        
        # In a real implementation, this would create a SalesOrder entity 
        # and transfer data from the quote
        # For now, we'll just update the quote status and return success
        
        quote.status = QuoteStatus.CONVERTED
        quote.updated_at = datetime.now()
        quote.updated_by = str(current_user_id)
        
        try:
            # Get customer name for event
            customer = self.db.query(Customer).filter(Customer.id == quote.customer_id).first()
            customer_name = customer.display_name if customer else "Unknown Customer"
            
            # Create a mock order ID and number for the event
            order_id = uuid.uuid4()
            order_number = f"SO-{uuid.uuid4().hex[:8].upper()}"
            
            # Dispatch quote converted event
            self.event_dispatcher.dispatch(
                QuoteConvertedToOrderEvent(
                    quote_id=quote.id,
                    quote_number=quote.quote_number,
                    order_id=order_id,
                    order_number=order_number,
                    customer_id=quote.customer_id,
                    customer_name=customer_name,
                    total_amount=float(quote.total_amount),
                    company_id=quote.company_id,
                    user_id=current_user_id
                )
            )
            
            # Commit changes
            self.db.commit()
            
            return {
                "success": True, 
                "message": "Quote converted to order successfully", 
                "quote_id": str(quote.id),
                "order_id": str(order_id),
                "order_number": order_number
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error converting quote to order: {str(e)}")
            raise
    
    # Analytics operations
    
    async def get_quote_analytics(self, company_id: UUID) -> Dict[str, Any]:
        """Get analytics data for quotes"""
        # Calculate total quotes by status
        status_counts = (
            self.db.query(
                Quote.status,
                func.count(Quote.id).label("count")
            )
            .filter(Quote.company_id == company_id)
            .group_by(Quote.status)
            .all()
        )
        
        # Calculate conversion rate
        total_quotes = sum(count for _, count in status_counts)
        accepted_quotes = next((count for status, count in status_counts if status == QuoteStatus.ACCEPTED), 0)
        converted_quotes = next((count for status, count in status_counts if status == QuoteStatus.CONVERTED), 0)
        
        conversion_rate = 0
        if total_quotes > 0:
            conversion_rate = (accepted_quotes + converted_quotes) / total_quotes * 100
        
        # Calculate average quote value
        avg_value = (
            self.db.query(func.avg(Quote.total_amount).label("avg_value"))
            .filter(Quote.company_id == company_id)
            .scalar() or 0
        )
        
        return {
            "total_quotes": total_quotes,
            "quotes_by_status": {status.value: count for status, count in status_counts},
            "conversion_rate": conversion_rate,
            "average_quote_value": float(avg_value)
        }
