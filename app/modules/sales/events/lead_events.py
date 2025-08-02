from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal
import logging
from abc import ABC, abstractmethod

# Set up logging
logger = logging.getLogger(__name__)


class LeadEvent(ABC):
    """Base class for all lead-related events"""
    event_type: str
    timestamp: datetime
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        pass


class LeadCreatedEvent(LeadEvent):
    """Event fired when a new lead is created"""
    event_type = "lead.created"
    
    def __init__(
        self, 
        lead_id: str, 
        lead_code: str, 
        display_name: str,
        lead_type: str,
        source: Optional[str],
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.lead_id = lead_id
        self.lead_code = lead_code
        self.display_name = display_name
        self.lead_type = lead_type
        self.source = source
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "lead_id": self.lead_id,
                "lead_code": self.lead_code,
                "display_name": self.display_name,
                "lead_type": self.lead_type,
                "source": self.source,
                "company_id": str(self.company_id),
                "created_by": str(self.user_id)
            }
        }


class LeadUpdatedEvent(LeadEvent):
    """Event fired when a lead is updated"""
    event_type = "lead.updated"
    
    def __init__(
        self, 
        lead_id: str, 
        lead_code: str, 
        display_name: str,
        lead_type: str,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.lead_id = lead_id
        self.lead_code = lead_code
        self.display_name = display_name
        self.lead_type = lead_type
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "lead_id": self.lead_id,
                "lead_code": self.lead_code,
                "display_name": self.display_name,
                "lead_type": self.lead_type,
                "company_id": str(self.company_id),
                "updated_by": str(self.user_id)
            }
        }


class LeadStatusChangedEvent(LeadEvent):
    """Event fired when a lead's status changes"""
    event_type = "lead.status_changed"
    
    def __init__(
        self, 
        lead_id: str, 
        lead_code: str, 
        display_name: str,
        old_status: str,
        new_status: str,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.lead_id = lead_id
        self.lead_code = lead_code
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
                "lead_id": self.lead_id,
                "lead_code": self.lead_code,
                "display_name": self.display_name,
                "old_status": self.old_status,
                "new_status": self.new_status,
                "company_id": str(self.company_id),
                "updated_by": str(self.user_id)
            }
        }


class LeadQualificationChangedEvent(LeadEvent):
    """Event fired when a lead's qualification status changes"""
    event_type = "lead.qualification_changed"
    
    def __init__(
        self, 
        lead_id: str, 
        lead_code: str, 
        display_name: str,
        old_qualification: str,
        new_qualification: str,
        lead_score: Optional[int],
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.lead_id = lead_id
        self.lead_code = lead_code
        self.display_name = display_name
        self.old_qualification = old_qualification
        self.new_qualification = new_qualification
        self.lead_score = lead_score
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "lead_id": self.lead_id,
                "lead_code": self.lead_code,
                "display_name": self.display_name,
                "old_qualification": self.old_qualification,
                "new_qualification": self.new_qualification,
                "lead_score": self.lead_score,
                "company_id": str(self.company_id),
                "updated_by": str(self.user_id)
            }
        }


class LeadAssignedEvent(LeadEvent):
    """Event fired when a lead is assigned to a sales rep"""
    event_type = "lead.assigned"
    
    def __init__(
        self, 
        lead_id: str, 
        lead_code: str, 
        display_name: str,
        sales_rep_id: UUID,
        sales_rep_name: str,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.lead_id = lead_id
        self.lead_code = lead_code
        self.display_name = display_name
        self.sales_rep_id = sales_rep_id
        self.sales_rep_name = sales_rep_name
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "lead_id": self.lead_id,
                "lead_code": self.lead_code,
                "display_name": self.display_name,
                "sales_rep_id": str(self.sales_rep_id),
                "sales_rep_name": self.sales_rep_name,
                "company_id": str(self.company_id),
                "assigned_by": str(self.user_id)
            }
        }


class LeadConvertedEvent(LeadEvent):
    """Event fired when a lead is converted to a customer"""
    event_type = "lead.converted"
    
    def __init__(
        self, 
        lead_id: str, 
        lead_code: str, 
        display_name: str,
        customer_id: str,
        customer_code: str,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.lead_id = lead_id
        self.lead_code = lead_code
        self.display_name = display_name
        self.customer_id = customer_id
        self.customer_code = customer_code
        self.company_id = company_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": {
                "lead_id": self.lead_id,
                "lead_code": self.lead_code,
                "display_name": self.display_name,
                "customer_id": self.customer_id,
                "customer_code": self.customer_code,
                "company_id": str(self.company_id),
                "converted_by": str(self.user_id)
            }
        }


class LeadActivityAddedEvent(LeadEvent):
    """Event fired when an activity is added to a lead"""
    event_type = "lead.activity_added"
    
    def __init__(
        self, 
        lead_id: str, 
        lead_code: str, 
        display_name: str,
        activity_id: UUID,
        activity_type: str,
        activity_subject: str,
        company_id: UUID, 
        user_id: UUID,
        timestamp: Optional[datetime] = None
    ):
        self.lead_id = lead_id
        self.lead_code = lead_code
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
                "lead_id": self.lead_id,
                "lead_code": self.lead_code,
                "display_name": self.display_name,
                "activity_id": str(self.activity_id),
                "activity_type": self.activity_type,
                "activity_subject": self.activity_subject,
                "company_id": str(self.company_id),
                "created_by": str(self.user_id)
            }
        }


class LeadEventDispatcher:
    """Dispatcher for lead-related events"""
    
    def __init__(self):
        # Event handlers could be registered here
        self._handlers = {}
    
    def dispatch(self, event: LeadEvent):
        """Dispatch event to all registered handlers"""
        event_dict = event.to_dict()
        logger.info(f"Dispatching lead event: {event.event_type}")
        
        # Log the event for debugging
        logger.debug(f"Event data: {event_dict}")
        
        # Call registered handlers
        if event.event_type in self._handlers:
            for handler in self._handlers[event.event_type]:
                try:
                    handler(event_dict)
                except Exception as e:
                    logger.error(f"Error in event handler for {event.event_type}: {e}")
