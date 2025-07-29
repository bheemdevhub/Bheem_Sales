from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal
import logging
from abc import ABC, abstractmethod

# Set up logging
logger = logging.getLogger(__name__)


class VendorEvent(ABC):
    """Base class for all vendor-related events"""
    event_type: str
    timestamp: datetime
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        pass


class VendorCreatedEvent(VendorEvent):
    """Event fired when a new vendor is created"""
    event_type = "vendor.created"
    
    def __init__(
        self, 
        vendor_id: str, 
        vendor_code: str, 
        display_name: str,
        vendor_type: str,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.vendor_id = vendor_id
        self.vendor_code = vendor_code
        self.display_name = display_name
        self.vendor_type = vendor_type
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "vendor_id": self.vendor_id,
                "vendor_code": self.vendor_code,
                "display_name": self.display_name,
                "vendor_type": self.vendor_type,
                "company_id": str(self.company_id),
                "created_by": str(self.user_id)
            }
        }


class VendorUpdatedEvent(VendorEvent):
    """Event fired when a vendor is updated"""
    event_type = "vendor.updated"
    
    def __init__(
        self, 
        vendor_id: str, 
        vendor_code: str, 
        display_name: str,
        vendor_type: str,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.vendor_id = vendor_id
        self.vendor_code = vendor_code
        self.display_name = display_name
        self.vendor_type = vendor_type
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "vendor_id": self.vendor_id,
                "vendor_code": self.vendor_code,
                "display_name": self.display_name,
                "vendor_type": self.vendor_type,
                "company_id": str(self.company_id),
                "updated_by": str(self.user_id)
            }
        }


class VendorStatusChangedEvent(VendorEvent):
    """Event fired when a vendor's status changes"""
    event_type = "vendor.status_changed"
    
    def __init__(
        self, 
        vendor_id: str, 
        vendor_code: str, 
        display_name: str,
        old_status: str,
        new_status: str,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.vendor_id = vendor_id
        self.vendor_code = vendor_code
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
                "vendor_id": self.vendor_id,
                "vendor_code": self.vendor_code,
                "display_name": self.display_name,
                "old_status": self.old_status,
                "new_status": self.new_status,
                "company_id": str(self.company_id),
                "updated_by": str(self.user_id)
            }
        }


class VendorRatingUpdatedEvent(VendorEvent):
    """Event fired when a vendor's ratings are updated"""
    event_type = "vendor.rating_updated"
    
    def __init__(
        self, 
        vendor_id: str, 
        vendor_code: str, 
        display_name: str,
        quality_rating: Optional[float],
        delivery_rating: Optional[float],
        service_rating: Optional[float],
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.vendor_id = vendor_id
        self.vendor_code = vendor_code
        self.display_name = display_name
        self.quality_rating = quality_rating
        self.delivery_rating = delivery_rating
        self.service_rating = service_rating
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "vendor_id": self.vendor_id,
                "vendor_code": self.vendor_code,
                "display_name": self.display_name,
                "quality_rating": self.quality_rating,
                "delivery_rating": self.delivery_rating,
                "service_rating": self.service_rating,
                "company_id": str(self.company_id),
                "updated_by": str(self.user_id)
            }
        }


class VendorActivityAddedEvent(VendorEvent):
    """Event fired when an activity is added to a vendor"""
    event_type = "vendor.activity_added"
    
    def __init__(
        self, 
        vendor_id: str, 
        vendor_code: str, 
        display_name: str,
        activity_id: UUID,
        activity_type: str,
        activity_subject: str,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.vendor_id = vendor_id
        self.vendor_code = vendor_code
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
                "vendor_id": self.vendor_id,
                "vendor_code": self.vendor_code,
                "display_name": self.display_name,
                "activity_id": str(self.activity_id),
                "activity_type": self.activity_type,
                "activity_subject": self.activity_subject,
                "company_id": str(self.company_id),
                "created_by": str(self.user_id)
            }
        }


class VendorEventDispatcher:
    """Dispatcher for vendor-related events"""
    
    def __init__(self):
        # Event handlers could be registered here
        self._handlers = {}
    
    def dispatch(self, event: VendorEvent):
        """Dispatch event to all registered handlers"""
        event_dict = event.to_dict()
        logger.info(f"Dispatching vendor event: {event.event_type}")
        
        # Log the event for debugging
        logger.debug(f"Event data: {event_dict}")
        
        # Call registered handlers
        if event.event_type in self._handlers:
            for handler in self._handlers[event.event_type]:
                try:
                    handler(event_dict)
                except Exception as e:
                    logger.error(f"Error in event handler for {event.event_type}: {e}")
