# app/modules/sales/config.py
"""Sales Module Configuration"""

from enum import Enum
from typing import Dict, Any


class SalesEventTypes:
    """Sales module event types"""
    QUOTE_CREATED = "sales.quote.created"
    QUOTE_SENT = "sales.quote.sent"
    QUOTE_ACCEPTED = "sales.quote.accepted"
    QUOTE_REJECTED = "sales.quote.rejected"
    QUOTE_EXPIRED = "sales.quote.expired"
    
    ORDER_CREATED = "sales.order.created"
    ORDER_CONFIRMED = "sales.order.confirmed"
    ORDER_SHIPPED = "sales.order.shipped"
    ORDER_DELIVERED = "sales.order.delivered"
    ORDER_CANCELLED = "sales.order.cancelled"
    
    INVOICE_CREATED = "sales.invoice.created"
    INVOICE_SENT = "sales.invoice.sent"
    INVOICE_PAID = "sales.invoice.paid"
    INVOICE_OVERDUE = "sales.invoice.overdue"
    INVOICE_CANCELLED = "sales.invoice.cancelled"
    
    PAYMENT_RECEIVED = "sales.payment.received"
    PAYMENT_FAILED = "sales.payment.failed"
    PAYMENT_REFUNDED = "sales.payment.refunded"
    
    CUSTOMER_CREATED = "sales.customer.created"
    CUSTOMER_UPDATED = "sales.customer.updated"
    
    COMMISSION_CALCULATED = "sales.commission.calculated"
    COMMISSION_PAID = "sales.commission.paid"


class SalesSettings:
    """Sales module default settings"""
    
    # Quote settings
    QUOTE_VALIDITY_DAYS = 30
    QUOTE_NUMBER_PREFIX = "QT"
    AUTO_SEND_QUOTES = False
    
    # Order settings
    ORDER_NUMBER_PREFIX = "SO"
    AUTO_CONFIRM_ORDERS = False
    REQUIRE_SHIPPING_ADDRESS = True
    
    # Invoice settings
    INVOICE_NUMBER_PREFIX = "INV"
    DEFAULT_PAYMENT_TERMS = 30  # Days
    AUTO_SEND_INVOICES = True
    LATE_FEE_RATE = 1.5  # Percentage
    
    # Payment settings
    ALLOW_PARTIAL_PAYMENTS = True
    AUTO_APPLY_PAYMENTS = True
    PAYMENT_GRACE_PERIOD = 5  # Days
    
    # Commission settings
    DEFAULT_COMMISSION_RATE = 5.0  # Percentage
    COMMISSION_ON_PAYMENT = True  # Calculate commission when payment received
    
    # Integration settings
    SYNC_WITH_CRM = True
    SYNC_WITH_ACCOUNTING = True
    SYNC_WITH_INVENTORY = True


# Sales permissions for role-based access control
SALES_PERMISSIONS = {
    # Quote permissions
    "sales.create_quote": "Create sales quotes",
    "sales.update_quote": "Update sales quotes", 
    "sales.view_quote": "View sales quotes",
    "sales.delete_quote": "Delete sales quotes",
    "sales.approve_quote": "Approve sales quotes",
    "sales.convert_quote": "Convert quotes to orders",
    "sales.send_quote": "Send quotes to customers",
    
    # Order permissions
    "sales.create_order": "Create sales orders",
    "sales.update_order": "Update sales orders",
    "sales.view_order": "View sales orders",
    "sales.cancel_order": "Cancel sales orders",
    "sales.fulfill_order": "Fulfill sales orders",
    "sales.partial_fulfill": "Partial fulfillment of orders",
    "sales.ship_order": "Ship sales orders",
    
    # Invoice permissions
    "sales.create_invoice": "Create sales invoices",
    "sales.update_invoice": "Update sales invoices",
    "sales.view_invoice": "View sales invoices",
    "sales.send_invoice": "Send invoices to customers",
    "sales.void_invoice": "Void sales invoices",
    "sales.create_credit_note": "Create credit notes",
    
    # Customer permissions
    "sales.create_customer": "Create customers",
    "sales.update_customer": "Update customer information",
    "sales.view_customer": "View customer information",
    "sales.delete_customer": "Delete customers",
    "sales.manage_customer_credit": "Manage customer credit limits",
    
    # Product permissions
    "sales.view_products": "View product catalog",
    "sales.manage_pricing": "Manage product pricing",
    "sales.create_bundles": "Create product bundles",
    "sales.manage_discounts": "Manage discounts and promotions",
    
    # Payment permissions
    "sales.record_payment": "Record customer payments",
    "sales.process_refund": "Process customer refunds",
    "sales.view_payment_history": "View payment history",
    
    # Analytics permissions
    "sales.view_reports": "View sales reports",
    "sales.view_analytics": "View sales analytics",
    "sales.export_data": "Export sales data",
    
    # Commission permissions
    "sales.view_commissions": "View sales commissions",
    "sales.calculate_commissions": "Calculate sales commissions",
    "sales.pay_commissions": "Process commission payments",
    
    # Admin permissions
    "sales.admin_settings": "Manage sales module settings",
    "sales.manage_sales_team": "Manage sales team members",
    "sales.configure_workflows": "Configure sales workflows",
    "sales.manage_integrations": "Manage sales integrations",
    
    # Custom SKU permissions
    "sku.custom.create": "Create custom SKU types",
    "sku.custom.read": "View custom SKU types",
    "sku.custom.update": "Update custom SKU types",
    "sku.custom.delete": "Delete custom SKU types",
    "sku.custom.validate": "Validate custom SKU data",
    "sku.custom.analytics": "View custom SKU analytics",
    
    # Custom SKU Instance permissions
    "sku.custom.instance.create": "Create custom SKU instances",
    "sku.custom.instance.read": "View custom SKU instances",
    "sku.custom.instance.update": "Update custom SKU instances",
    "sku.custom.instance.delete": "Delete custom SKU instances",
    "sku.custom.instance.bulk_create": "Bulk create custom SKU instances",
    "sku.custom.analytics": "View custom SKU analytics",
    
    # Custom SKU Instance permissions
    "sku.custom.instance.create": "Create custom SKU instances",
    "sku.custom.instance.read": "View custom SKU instances",
    "sku.custom.instance.update": "Update custom SKU instances",
    "sku.custom.instance.delete": "Delete custom SKU instances",
    "sku.custom.instance.bulk_create": "Bulk create custom SKU instances",
}


class SalesDocumentTypes:
    """Document types for sales module"""
    QUOTE = "QUOTE"
    ORDER = "ORDER"
    INVOICE = "INVOICE"
    RECEIPT = "RECEIPT"
    CREDIT_NOTE = "CREDIT_NOTE"
    DELIVERY_NOTE = "DELIVERY_NOTE"


class SalesNotificationTypes:
    """Notification types for sales events"""
    QUOTE_EXPIRING = "quote_expiring"
    ORDER_CONFIRMED = "order_confirmed"
    INVOICE_OVERDUE = "invoice_overdue"
    PAYMENT_RECEIVED = "payment_received"
    LOW_STOCK_ALERT = "low_stock_alert"
    COMMISSION_READY = "commission_ready"


class SalesIntegrationSettings:
    """Integration settings with other modules"""
    
    # CRM Integration
    CRM_SYNC_CUSTOMERS = True
    CRM_SYNC_OPPORTUNITIES = True
    CRM_CREATE_ACTIVITIES = True
    
    # Accounting Integration
    ACCOUNTING_AUTO_POST = True
    ACCOUNTING_REVENUE_ACCOUNT = "4000"
    ACCOUNTING_AR_ACCOUNT = "1200"
    ACCOUNTING_TAX_ACCOUNT = "2300"
    
    # Inventory Integration
    INVENTORY_AUTO_RESERVE = True
    INVENTORY_AUTO_ALLOCATE = True
    INVENTORY_CHECK_AVAILABILITY = True
    
    # Email Integration
    EMAIL_QUOTE_TEMPLATE = "quote_template"
    EMAIL_ORDER_TEMPLATE = "order_confirmation_template"
    EMAIL_INVOICE_TEMPLATE = "invoice_template"
    EMAIL_PAYMENT_TEMPLATE = "payment_receipt_template"
