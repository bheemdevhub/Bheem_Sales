from typing import Dict, Any
from datetime import datetime
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

class SalesInvoiceEvent:
    event_type: str
    timestamp: datetime
    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError

class SalesInvoiceCreatedEvent(SalesInvoiceEvent):
    event_type = "sales_invoice.created"
    # ...fields...
    def to_dict(self):
        return {"event_type": self.event_type, "timestamp": self.timestamp.isoformat(), "data": {...}}

class SalesInvoiceSentEvent(SalesInvoiceEvent):
    event_type = "sales_invoice.sent"
    # ...fields...
    def to_dict(self):
        return {"event_type": self.event_type, "timestamp": self.timestamp.isoformat(), "data": {...}}

class SalesInvoiceVoidedEvent(SalesInvoiceEvent):
    event_type = "sales_invoice.voided"
    # ...fields...
    def to_dict(self):
        return {"event_type": self.event_type, "timestamp": self.timestamp.isoformat(), "data": {...}}

class SalesInvoiceEventDispatcher:
    def __init__(self):
        self._handlers = {}
    def dispatch(self, event: SalesInvoiceEvent):
        logger.info(f"Dispatching event: {event.event_type}")
        # ...call handlers...
