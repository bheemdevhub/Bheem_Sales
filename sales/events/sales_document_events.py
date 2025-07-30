from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal
import logging
from abc import ABC, abstractmethod

# Set up logging
logger = logging.getLogger(__name__)


class SalesDocumentEvent(ABC):
    """Base class for all sales document-related events"""
    event_type: str
    timestamp: datetime
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        pass


# Quote Events

class QuoteCreatedEvent(SalesDocumentEvent):
    """Event fired when a new quote is created"""
    event_type = "quote.created"
    
    def __init__(
        self, 
        quote_id: UUID, 
        quote_number: str,
        customer_id: str,
        customer_name: str,
        total_amount: float,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.quote_id = quote_id
        self.quote_number = quote_number
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.total_amount = total_amount
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "quote_id": str(self.quote_id),
                "quote_number": self.quote_number,
                "customer_id": self.customer_id,
                "customer_name": self.customer_name,
                "total_amount": self.total_amount,
                "company_id": str(self.company_id),
                "created_by": str(self.user_id)
            }
        }


class QuoteUpdatedEvent(SalesDocumentEvent):
    """Event fired when a quote is updated"""
    event_type = "quote.updated"
    
    def __init__(
        self, 
        quote_id: UUID, 
        quote_number: str,
        customer_id: str,
        customer_name: str,
        total_amount: float,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.quote_id = quote_id
        self.quote_number = quote_number
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.total_amount = total_amount
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "quote_id": str(self.quote_id),
                "quote_number": self.quote_number,
                "customer_id": self.customer_id,
                "customer_name": self.customer_name,
                "total_amount": self.total_amount,
                "company_id": str(self.company_id),
                "updated_by": str(self.user_id)
            }
        }


class QuoteStatusChangedEvent(SalesDocumentEvent):
    """Event fired when a quote's status changes"""
    event_type = "quote.status_changed"
    
    def __init__(
        self, 
        quote_id: UUID, 
        quote_number: str,
        customer_id: str,
        customer_name: str,
        old_status: str,
        new_status: str,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.quote_id = quote_id
        self.quote_number = quote_number
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.old_status = old_status
        self.new_status = new_status
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "quote_id": str(self.quote_id),
                "quote_number": self.quote_number,
                "customer_id": self.customer_id,
                "customer_name": self.customer_name,
                "old_status": self.old_status,
                "new_status": self.new_status,
                "company_id": str(self.company_id),
                "updated_by": str(self.user_id)
            }
        }


class QuoteSentEvent(SalesDocumentEvent):
    """Event fired when a quote is sent to a customer"""
    event_type = "quote.sent"
    
    def __init__(
        self, 
        quote_id: UUID, 
        quote_number: str,
        customer_id: str,
        customer_name: str,
        sent_to: str,
        total_amount: float,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.quote_id = quote_id
        self.quote_number = quote_number
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.sent_to = sent_to
        self.total_amount = total_amount
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "quote_id": str(self.quote_id),
                "quote_number": self.quote_number,
                "customer_id": self.customer_id,
                "customer_name": self.customer_name,
                "sent_to": self.sent_to,
                "total_amount": self.total_amount,
                "company_id": str(self.company_id),
                "sent_by": str(self.user_id)
            }
        }


class QuoteAcceptedEvent(SalesDocumentEvent):
    """Event fired when a quote is accepted by a customer"""
    event_type = "quote.accepted"
    
    def __init__(
        self, 
        quote_id: UUID, 
        quote_number: str,
        customer_id: str,
        customer_name: str,
        total_amount: float,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.quote_id = quote_id
        self.quote_number = quote_number
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.total_amount = total_amount
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "quote_id": str(self.quote_id),
                "quote_number": self.quote_number,
                "customer_id": self.customer_id,
                "customer_name": self.customer_name,
                "total_amount": self.total_amount,
                "company_id": str(self.company_id),
                "accepted_by": str(self.user_id)
            }
        }


class QuoteRejectedEvent(SalesDocumentEvent):
    """Event fired when a quote is rejected by a customer"""
    event_type = "quote.rejected"
    
    def __init__(
        self, 
        quote_id: UUID, 
        quote_number: str,
        customer_id: str,
        customer_name: str,
        reason: Optional[str],
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.quote_id = quote_id
        self.quote_number = quote_number
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.reason = reason
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "quote_id": str(self.quote_id),
                "quote_number": self.quote_number,
                "customer_id": self.customer_id,
                "customer_name": self.customer_name,
                "reason": self.reason,
                "company_id": str(self.company_id),
                "rejected_by": str(self.user_id)
            }
        }


class QuoteConvertedToOrderEvent(SalesDocumentEvent):
    """Event fired when a quote is converted to a sales order"""
    event_type = "quote.converted_to_order"
    
    def __init__(
        self, 
        quote_id: UUID, 
        quote_number: str,
        order_id: UUID,
        order_number: str,
        customer_id: str,
        customer_name: str,
        total_amount: float,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.quote_id = quote_id
        self.quote_number = quote_number
        self.order_id = order_id
        self.order_number = order_number
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.total_amount = total_amount
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "quote_id": str(self.quote_id),
                "quote_number": self.quote_number,
                "order_id": str(self.order_id),
                "order_number": self.order_number,
                "customer_id": self.customer_id,
                "customer_name": self.customer_name,
                "total_amount": self.total_amount,
                "company_id": str(self.company_id),
                "converted_by": str(self.user_id)
            }
        }


# Sales Order Events

class SalesOrderCreatedEvent(SalesDocumentEvent):
    """Event fired when a new sales order is created"""
    event_type = "sales_order.created"
    
    def __init__(
        self, 
        order_id: UUID, 
        order_number: str,
        customer_id: str,
        customer_name: str,
        total_amount: float,
        quote_id: Optional[UUID],
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.order_id = order_id
        self.order_number = order_number
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.total_amount = total_amount
        self.quote_id = quote_id
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        data = {
            "order_id": str(self.order_id),
            "order_number": self.order_number,
            "customer_id": self.customer_id,
            "customer_name": self.customer_name,
            "total_amount": self.total_amount,
            "company_id": str(self.company_id),
            "created_by": str(self.user_id)
        }
        
        if self.quote_id:
            data["quote_id"] = str(self.quote_id)
            
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": data
        }


class SalesOrderUpdatedEvent(SalesDocumentEvent):
    """Event fired when a sales order is updated"""
    event_type = "sales_order.updated"
    
    def __init__(
        self, 
        order_id: UUID, 
        order_number: str,
        customer_id: str,
        customer_name: str,
        total_amount: float,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.order_id = order_id
        self.order_number = order_number
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.total_amount = total_amount
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "order_id": str(self.order_id),
                "order_number": self.order_number,
                "customer_id": self.customer_id,
                "customer_name": self.customer_name,
                "total_amount": self.total_amount,
                "company_id": str(self.company_id),
                "updated_by": str(self.user_id)
            }
        }


class SalesOrderStatusChangedEvent(SalesDocumentEvent):
    """Event fired when a sales order's status changes"""
    event_type = "sales_order.status_changed"
    
    def __init__(
        self, 
        order_id: UUID, 
        order_number: str,
        customer_id: str,
        customer_name: str,
        old_status: str,
        new_status: str,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.order_id = order_id
        self.order_number = order_number
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.old_status = old_status
        self.new_status = new_status
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "order_id": str(self.order_id),
                "order_number": self.order_number,
                "customer_id": self.customer_id,
                "customer_name": self.customer_name,
                "old_status": self.old_status,
                "new_status": self.new_status,
                "company_id": str(self.company_id),
                "updated_by": str(self.user_id)
            }
        }


class SalesOrderFulfilledEvent(SalesDocumentEvent):
    """Event fired when a sales order is fulfilled"""
    event_type = "sales_order.fulfilled"
    
    def __init__(
        self, 
        order_id: UUID, 
        order_number: str,
        customer_id: str,
        customer_name: str,
        fulfillment_date: date,
        shipping_info: Optional[Dict[str, Any]],
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.order_id = order_id
        self.order_number = order_number
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.fulfillment_date = fulfillment_date
        self.shipping_info = shipping_info or {}
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "order_id": str(self.order_id),
                "order_number": self.order_number,
                "customer_id": self.customer_id,
                "customer_name": self.customer_name,
                "fulfillment_date": self.fulfillment_date.isoformat(),
                "shipping_info": self.shipping_info,
                "company_id": str(self.company_id),
                "fulfilled_by": str(self.user_id)
            }
        }


class SalesOrderCancelledEvent(SalesDocumentEvent):
    """Event fired when a sales order is cancelled"""
    event_type = "sales_order.cancelled"
    
    def __init__(
        self, 
        order_id: UUID, 
        order_number: str,
        customer_id: str,
        customer_name: str,
        reason: Optional[str],
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.order_id = order_id
        self.order_number = order_number
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.reason = reason
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "order_id": str(self.order_id),
                "order_number": self.order_number,
                "customer_id": self.customer_id,
                "customer_name": self.customer_name,
                "reason": self.reason,
                "company_id": str(self.company_id),
                "cancelled_by": str(self.user_id)
            }
        }


class SalesOrderReturnedEvent(SalesDocumentEvent):
    """Event fired when a sales order is returned"""
    event_type = "sales_order.returned"
    
    def __init__(
        self, 
        order_id: UUID, 
        order_number: str,
        customer_id: str,
        customer_name: str,
        return_date: date,
        reason: Optional[str],
        items_returned: List[Dict[str, Any]],
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.order_id = order_id
        self.order_number = order_number
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.return_date = return_date
        self.reason = reason
        self.items_returned = items_returned
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "order_id": str(self.order_id),
                "order_number": self.order_number,
                "customer_id": self.customer_id,
                "customer_name": self.customer_name,
                "return_date": self.return_date.isoformat(),
                "reason": self.reason,
                "items_returned": self.items_returned,
                "company_id": str(self.company_id),
                "processed_by": str(self.user_id)
            }
        }


class SalesOrderInvoicedEvent(SalesDocumentEvent):
    """Event fired when a sales order is invoiced"""
    event_type = "sales_order.invoiced"
    
    def __init__(
        self, 
        order_id: UUID, 
        order_number: str,
        invoice_id: UUID,
        invoice_number: str,
        customer_id: str,
        customer_name: str,
        invoice_amount: float,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.order_id = order_id
        self.order_number = order_number
        self.invoice_id = invoice_id
        self.invoice_number = invoice_number
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.invoice_amount = invoice_amount
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "order_id": str(self.order_id),
                "order_number": self.order_number,
                "invoice_id": str(self.invoice_id),
                "invoice_number": self.invoice_number,
                "customer_id": self.customer_id,
                "customer_name": self.customer_name,
                "invoice_amount": self.invoice_amount,
                "company_id": str(self.company_id),
                "invoiced_by": str(self.user_id)
            }
        }


# Sales Invoice Events

class SalesInvoiceCreatedEvent(SalesDocumentEvent):
    """Event fired when a new sales invoice is created"""
    event_type = "sales_invoice.created"
    
    def __init__(
        self, 
        invoice_id: UUID, 
        invoice_number: str,
        customer_id: str,
        customer_name: str,
        total_amount: float,
        order_id: Optional[UUID],
        due_date: date,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.invoice_id = invoice_id
        self.invoice_number = invoice_number
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.total_amount = total_amount
        self.order_id = order_id
        self.due_date = due_date
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        data = {
            "invoice_id": str(self.invoice_id),
            "invoice_number": self.invoice_number,
            "customer_id": self.customer_id,
            "customer_name": self.customer_name,
            "total_amount": self.total_amount,
            "due_date": self.due_date.isoformat(),
            "company_id": str(self.company_id),
            "created_by": str(self.user_id)
        }
        
        if self.order_id:
            data["order_id"] = str(self.order_id)
            
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": data
        }


class SalesInvoiceUpdatedEvent(SalesDocumentEvent):
    """Event fired when a sales invoice is updated"""
    event_type = "sales_invoice.updated"
    
    def __init__(
        self, 
        invoice_id: UUID, 
        invoice_number: str,
        customer_id: str,
        customer_name: str,
        total_amount: float,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.invoice_id = invoice_id
        self.invoice_number = invoice_number
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.total_amount = total_amount
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "invoice_id": str(self.invoice_id),
                "invoice_number": self.invoice_number,
                "customer_id": self.customer_id,
                "customer_name": self.customer_name,
                "total_amount": self.total_amount,
                "company_id": str(self.company_id),
                "updated_by": str(self.user_id)
            }
        }


class SalesInvoiceStatusChangedEvent(SalesDocumentEvent):
    """Event fired when a sales invoice's status changes"""
    event_type = "sales_invoice.status_changed"
    
    def __init__(
        self, 
        invoice_id: UUID, 
        invoice_number: str,
        customer_id: str,
        customer_name: str,
        old_status: str,
        new_status: str,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.invoice_id = invoice_id
        self.invoice_number = invoice_number
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.old_status = old_status
        self.new_status = new_status
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "invoice_id": str(self.invoice_id),
                "invoice_number": self.invoice_number,
                "customer_id": self.customer_id,
                "customer_name": self.customer_name,
                "old_status": self.old_status,
                "new_status": self.new_status,
                "company_id": str(self.company_id),
                "updated_by": str(self.user_id)
            }
        }


class SalesInvoiceSentEvent(SalesDocumentEvent):
    """Event fired when a sales invoice is sent to a customer"""
    event_type = "sales_invoice.sent"
    
    def __init__(
        self, 
        invoice_id: UUID, 
        invoice_number: str,
        customer_id: str,
        customer_name: str,
        sent_to: str,
        total_amount: float,
        due_date: date,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.invoice_id = invoice_id
        self.invoice_number = invoice_number
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.sent_to = sent_to
        self.total_amount = total_amount
        self.due_date = due_date
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "invoice_id": str(self.invoice_id),
                "invoice_number": self.invoice_number,
                "customer_id": self.customer_id,
                "customer_name": self.customer_name,
                "sent_to": self.sent_to,
                "total_amount": self.total_amount,
                "due_date": self.due_date.isoformat(),
                "company_id": str(self.company_id),
                "sent_by": str(self.user_id)
            }
        }


class SalesInvoicePaidEvent(SalesDocumentEvent):
    """Event fired when a sales invoice is paid"""
    event_type = "sales_invoice.paid"
    
    def __init__(
        self, 
        invoice_id: UUID, 
        invoice_number: str,
        customer_id: str,
        customer_name: str,
        payment_id: UUID,
        payment_reference: str,
        payment_amount: float,
        payment_method: str,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.invoice_id = invoice_id
        self.invoice_number = invoice_number
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.payment_id = payment_id
        self.payment_reference = payment_reference
        self.payment_amount = payment_amount
        self.payment_method = payment_method
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "invoice_id": str(self.invoice_id),
                "invoice_number": self.invoice_number,
                "customer_id": self.customer_id,
                "customer_name": self.customer_name,
                "payment_id": str(self.payment_id),
                "payment_reference": self.payment_reference,
                "payment_amount": self.payment_amount,
                "payment_method": self.payment_method,
                "company_id": str(self.company_id),
                "recorded_by": str(self.user_id)
            }
        }


class SalesInvoiceOverdueEvent(SalesDocumentEvent):
    """Event fired when a sales invoice becomes overdue"""
    event_type = "sales_invoice.overdue"
    
    def __init__(
        self, 
        invoice_id: UUID, 
        invoice_number: str,
        customer_id: str,
        customer_name: str,
        due_date: date,
        days_overdue: int,
        balance_due: float,
        company_id: UUID, 
        timestamp: Optional[datetime] = None
    ):
        self.invoice_id = invoice_id
        self.invoice_number = invoice_number
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.due_date = due_date
        self.days_overdue = days_overdue
        self.balance_due = balance_due
        self.company_id = company_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "invoice_id": str(self.invoice_id),
                "invoice_number": self.invoice_number,
                "customer_id": self.customer_id,
                "customer_name": self.customer_name,
                "due_date": self.due_date.isoformat(),
                "days_overdue": self.days_overdue,
                "balance_due": self.balance_due,
                "company_id": str(self.company_id)
            }
        }


# Customer Payment Events

class CustomerPaymentCreatedEvent(SalesDocumentEvent):
    """Event fired when a new customer payment is created"""
    event_type = "customer_payment.created"
    
    def __init__(
        self, 
        payment_id: UUID, 
        payment_reference: str,
        customer_id: str,
        customer_name: str,
        invoice_id: Optional[UUID],
        invoice_number: Optional[str],
        payment_amount: float,
        payment_method: str,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.payment_id = payment_id
        self.payment_reference = payment_reference
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.invoice_id = invoice_id
        self.invoice_number = invoice_number
        self.payment_amount = payment_amount
        self.payment_method = payment_method
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        data = {
            "payment_id": str(self.payment_id),
            "payment_reference": self.payment_reference,
            "customer_id": self.customer_id,
            "customer_name": self.customer_name,
            "payment_amount": self.payment_amount,
            "payment_method": self.payment_method,
            "company_id": str(self.company_id),
            "created_by": str(self.user_id)
        }
        
        if self.invoice_id:
            data["invoice_id"] = str(self.invoice_id)
            data["invoice_number"] = self.invoice_number
            
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": data
        }


class CustomerPaymentStatusChangedEvent(SalesDocumentEvent):
    """Event fired when a customer payment's status changes"""
    event_type = "customer_payment.status_changed"
    
    def __init__(
        self, 
        payment_id: UUID, 
        payment_reference: str,
        customer_id: str,
        customer_name: str,
        old_status: str,
        new_status: str,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.payment_id = payment_id
        self.payment_reference = payment_reference
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.old_status = old_status
        self.new_status = new_status
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "payment_id": str(self.payment_id),
                "payment_reference": self.payment_reference,
                "customer_id": self.customer_id,
                "customer_name": self.customer_name,
                "old_status": self.old_status,
                "new_status": self.new_status,
                "company_id": str(self.company_id),
                "updated_by": str(self.user_id)
            }
        }


class CustomerPaymentAllocatedEvent(SalesDocumentEvent):
    """Event fired when a customer payment is allocated to an invoice"""
    event_type = "customer_payment.allocated"
    
    def __init__(
        self, 
        payment_id: UUID, 
        payment_reference: str,
        customer_id: str,
        customer_name: str,
        invoice_id: UUID,
        invoice_number: str,
        allocation_amount: float,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.payment_id = payment_id
        self.payment_reference = payment_reference
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.invoice_id = invoice_id
        self.invoice_number = invoice_number
        self.allocation_amount = allocation_amount
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "payment_id": str(self.payment_id),
                "payment_reference": self.payment_reference,
                "customer_id": self.customer_id,
                "customer_name": self.customer_name,
                "invoice_id": str(self.invoice_id),
                "invoice_number": self.invoice_number,
                "allocation_amount": self.allocation_amount,
                "company_id": str(self.company_id),
                "allocated_by": str(self.user_id)
            }
        }


class SalesDocumentEventDispatcher:
    """Dispatcher for sales document-related events"""
    
    def __init__(self):
        # Event handlers could be registered here
        self._handlers = {}
    
    def dispatch(self, event: SalesDocumentEvent):
        """Dispatch event to all registered handlers"""
        event_dict = event.to_dict()
        logger.info(f"Dispatching sales document event: {event.event_type}")
        
        # Log the event for debugging
        logger.debug(f"Event data: {event_dict}")
        
        # Call registered handlers
        if event.event_type in self._handlers:
            for handler in self._handlers[event.event_type]:
                try:
                    handler(event_dict)
                except Exception as e:
                    logger.error(f"Error in event handler for {event.event_type}: {e}")

