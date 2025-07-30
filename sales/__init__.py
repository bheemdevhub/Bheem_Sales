# app/modules/sales/__init__.py

"""Sales Management Module for Revenue Generation"""

from .module import SalesModule

from .core.models.sales_models import (
    Customer, Quote, QuoteLineItem, 
    SalesOrder, SalesOrderLineItem,
    SalesInvoice, SalesInvoiceLineItem,
    CustomerPayment, SalesCommission
)

# Import shared models for easy access
from bheem_core.shared.models import (
    Activity, SKU, SKUStatus, SKUCategory, SKUSubcategory, 
    SKUBillingType, SKUUnitType, Tag, Rating, FinancialDocument
)

__all__ = [
    "SalesModule",
    
    
    # Sales Models
    "Customer", "Quote", "QuoteLineItem",
    "SalesOrder", "SalesOrderLineItem",
    "SalesInvoice", "SalesInvoiceLineItem",
    "CustomerPayment", "SalesCommission",
    
    # Shared Models
    "Activity", "SKU", "SKUStatus", "SKUCategory", "SKUSubcategory",
    "SKUBillingType", "SKUUnitType", "Tag", "Rating", "FinancialDocument"
]


