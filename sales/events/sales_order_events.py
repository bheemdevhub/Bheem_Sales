from typing import Dict, Any
from datetime import datetime
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

class SalesOrderEvent:
    event_type: str
    timestamp: datetime
    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError

class SalesOrderCreatedEvent(SalesOrderEvent):
    event_type = "sales_order.created"
    # ...fields...
    def to_dict(self):
        return {"event_type": self.event_type, "timestamp": self.timestamp.isoformat(), "data": {...}}

class SalesOrderUpdatedEvent(SalesOrderEvent):
    event_type = "sales_order.updated"
    # ...fields...
    def to_dict(self):
        return {"event_type": self.event_type, "timestamp": self.timestamp.isoformat(), "data": {...}}

class SalesOrderShippedEvent(SalesOrderEvent):
    event_type = "sales_order.shipped"
    # ...fields...
    def to_dict(self):
        return {"event_type": self.event_type, "timestamp": self.timestamp.isoformat(), "data": {...}}

class SalesOrderCancelledEvent(SalesOrderEvent):
    event_type = "sales_order.cancelled"
    # ...fields...
    def to_dict(self):
        return {"event_type": self.event_type, "timestamp": self.timestamp.isoformat(), "data": {...}}

class SalesOrderEventDispatcher:
    def __init__(self):
        self._handlers = {}
    def dispatch(self, event: SalesOrderEvent):
        logger.info(f"Dispatching event: {event.event_type}")
        # ...call handlers...
