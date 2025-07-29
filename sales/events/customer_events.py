from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal
import logging
from abc import ABC, abstractmethod

# Set up logging
logger = logging.getLogger(__name__)


class CustomerEvent(ABC):
    """Base class for all customer-related events"""
    event_type: str
    timestamp: datetime
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        pass


class CustomerCreatedEvent(CustomerEvent):
    """Event fired when a new customer is created"""
    event_type = "customer.created"
    
    def __init__(
        self, 
        customer_id: str, 
        customer_code: str, 
        display_name: str,
        customer_type: str,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.customer_id = customer_id
        self.customer_code = customer_code
        self.display_name = display_name
        self.customer_type = customer_type
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "customer_id": self.customer_id,
                "customer_code": self.customer_code,
                "display_name": self.display_name,
                "customer_type": self.customer_type,
                "company_id": str(self.company_id),
                "created_by": str(self.user_id)
            }
        }


class CustomerUpdatedEvent(CustomerEvent):
    """Event fired when a customer is updated"""
    event_type = "customer.updated"
    
    def __init__(
        self, 
        customer_id: str, 
        customer_code: str, 
        display_name: str,
        customer_type: str,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.customer_id = customer_id
        self.customer_code = customer_code
        self.display_name = display_name
        self.customer_type = customer_type
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "customer_id": self.customer_id,
                "customer_code": self.customer_code,
                "display_name": self.display_name,
                "customer_type": self.customer_type,
                "company_id": str(self.company_id),
                "updated_by": str(self.user_id)
            }
        }


class CustomerStatusChangedEvent(CustomerEvent):
    """Event fired when a customer's status changes"""
    event_type = "customer.status_changed"
    
    def __init__(
        self, 
        customer_id: str, 
        customer_code: str, 
        display_name: str,
        old_status: str,
        new_status: str,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.customer_id = customer_id
        self.customer_code = customer_code
        self.display_name = display_name
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
                "customer_id": self.customer_id,
                "customer_code": self.customer_code,
                "display_name": self.display_name,
                "old_status": self.old_status,
                "new_status": self.new_status,
                "company_id": str(self.company_id),
                "updated_by": str(self.user_id)
            }
        }


class CustomerCreditLimitChangedEvent(CustomerEvent):
    """Event fired when a customer's credit limit is changed"""
    event_type = "customer.credit_limit_changed"
    
    def __init__(
        self, 
        customer_id: str, 
        customer_code: str, 
        display_name: str,
        old_credit_limit: float,
        new_credit_limit: float,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.customer_id = customer_id
        self.customer_code = customer_code
        self.display_name = display_name
        self.old_credit_limit = old_credit_limit
        self.new_credit_limit = new_credit_limit
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "customer_id": self.customer_id,
                "customer_code": self.customer_code,
                "display_name": self.display_name,
                "old_credit_limit": self.old_credit_limit,
                "new_credit_limit": self.new_credit_limit,
                "company_id": str(self.company_id),
                "updated_by": str(self.user_id)
            }
        }


class CustomerActivityAddedEvent(CustomerEvent):
    """Event fired when an activity is added to a customer"""
    event_type = "customer.activity_added"
    
    def __init__(
        self, 
        customer_id: str, 
        customer_code: str, 
        display_name: str,
        activity_id: UUID,
        activity_type: str,
        activity_subject: str,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.customer_id = customer_id
        self.customer_code = customer_code
        self.display_name = display_name
        self.activity_id = activity_id
        self.activity_type = activity_type
        self.activity_subject = activity_subject
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "customer_id": self.customer_id,
                "customer_code": self.customer_code,
                "display_name": self.display_name,
                "activity_id": str(self.activity_id),
                "activity_type": self.activity_type,
                "activity_subject": self.activity_subject,
                "company_id": str(self.company_id),
                "created_by": str(self.user_id)
            }
        }


class CustomerEventDispatcher:
    """Dispatcher for customer-related events"""
    
    def __init__(self):
        # Event handlers could be registered here
        self._handlers = {}
    
    def dispatch(self, event: CustomerEvent):
        """Dispatch event to all registered handlers"""
        event_dict = event.to_dict()
        logger.info(f"Dispatching customer event: {event.event_type}")
        
        # Log the event for debugging
        logger.debug(f"Event data: {event_dict}")
        
        # Call registered handlers
        if event.event_type in self._handlers:
            for handler in self._handlers[event.event_type]:
                try:
                    handler(event_dict)
                except Exception as e:
                    logger.error(f"Error in event handler for {event.event_type}: {e}")
