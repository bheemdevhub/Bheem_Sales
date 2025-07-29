"""Sales module database models"""

from sqlalchemy import Column, String, Text, Numeric, Date, DateTime, ForeignKey, JSON, Enum, Integer, Boolean, UniqueConstraint, Index, func, DECIMAL
from sqlalchemy.dialects.postgresql import UUID, ENUM as PGEnum, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.shared.models import BaseModel, Person, AuditMixin, Activity, ActivityType, ActivityStatus, FinancialDocument, DocumentType, DocumentStatus, Rating, RatingType, Tag, TagCategory, SKU, SKUStatus
import enum
import uuid
from datetime import datetime


SCHEMA = "sales"


# -----------------------------
# Sales Enums
# -----------------------------

# -----------------------------
# Sales-specific Enums
# -----------------------------

class CustomerType(str, enum.Enum):
    INDIVIDUAL = "INDIVIDUAL"
    BUSINESS = "BUSINESS"
    GOVERNMENT = "GOVERNMENT"
    NON_PROFIT = "NON_PROFIT"


class CustomerStatus(str, enum.Enum):
    PROSPECT = "PROSPECT"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    VIP = "VIP"
    BLOCKED = "BLOCKED"


class QuoteStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SENT = "SENT"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class OrderStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    RETURNED = "RETURNED"


class InvoiceStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SENT = "SENT"
    PAID = "PAID"
    PARTIAL_PAID = "PARTIAL_PAID"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"
    VOID = "VOID"


class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"
    CANCELLED = "CANCELLED"


class PaymentMethod(str, enum.Enum):
    CASH = "CASH"
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"
    BANK_TRANSFER = "BANK_TRANSFER"
    CHECK = "CHECK"
    DIGITAL_WALLET = "DIGITAL_WALLET"
    CRYPTOCURRENCY = "CRYPTOCURRENCY"


class DiscountType(str, enum.Enum):
    PERCENTAGE = "PERCENTAGE"
    FIXED_AMOUNT = "FIXED_AMOUNT"
    BUY_X_GET_Y = "BUY_X_GET_Y"


class LeadStatus(str, enum.Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    QUALIFIED = "QUALIFIED"
    DISQUALIFIED = "DISQUALIFIED"
    CONVERTED = "CONVERTED"
    CLOSED_LOST = "CLOSED_LOST"


class LeadSource(str, enum.Enum):
    WEBSITE = "WEBSITE"
    REFERRAL = "REFERRAL"
    COLD_CALL = "COLD_CALL"
    EMAIL_CAMPAIGN = "EMAIL_CAMPAIGN"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    TRADE_SHOW = "TRADE_SHOW"
    PARTNER = "PARTNER"
    ADVERTISEMENT = "ADVERTISEMENT"
    ORGANIC_SEARCH = "ORGANIC_SEARCH"
    PAID_SEARCH = "PAID_SEARCH"
    OTHER = "OTHER"


# -----------------------------
# Customer Model (Inherits from Person)
# -----------------------------

class Customer(Person):
    __tablename__ = "customers"
    __table_args__ = (
        {'schema': SCHEMA}
    )

    id = Column(UUID(as_uuid=True), ForeignKey("public.persons.id"), primary_key=True, default=uuid.uuid4)
    customer_code = Column(String(50), nullable=False)
    
    # Business information
    business_name = Column(String(255), nullable=True)  # For business customers
    industry = Column(String(100))
    customer_type = Column(PGEnum(CustomerType, name="customer_type_enum", create_type=False), 
                          default=CustomerType.INDIVIDUAL, nullable=False)
    customer_status = Column(PGEnum(CustomerStatus, name="customer_status_enum", create_type=False),
                           default=CustomerStatus.PROSPECT, nullable=False)
    tax_id = Column(String(50))
    
    # Financial information
    credit_limit = Column(Numeric(15, 2), default=0)
    payment_terms = Column(Integer, default=30)  # Days
    currency_id = Column(UUID(as_uuid=True), ForeignKey("public.currencies.id"))
    
    # CRM integration
    crm_contact_id = Column(UUID(as_uuid=True), ForeignKey("crm.crm_contacts.id"), nullable=True)  # Link to CRM contact
    
    # Sales information
    sales_rep_id = Column(UUID(as_uuid=True), ForeignKey("hr.employees.id"), nullable=True)  # Assigned sales representative

    # Add company_id column for multi-tenancy/ownership
    #company_id = Column(UUID(as_uuid=True), ForeignKey("public.companies.id", ondelete="SET NULL"), nullable=True)

    # Additional data
    tags = Column(JSON, nullable=True)  # JSON array of tags
    custom_fields = Column(JSON, nullable=True)  # Custom field values
    
    # Preferences
    preferred_communication = Column(String(50), default="EMAIL")  # EMAIL, PHONE, MAIL, etc.
    
    # Relationships
    sales_rep = relationship("Employee", foreign_keys=[sales_rep_id])
    crm_contact = relationship("CRMContact", foreign_keys=[crm_contact_id])
    quotes = relationship("Quote", back_populates="customer")
    orders = relationship("SalesOrder", back_populates="customer")
    invoices = relationship("SalesInvoice", back_populates="customer")
    payments = relationship("CustomerPayment", back_populates="customer")

    # Unified relationships using entity_type/entity_id pattern
    activities = relationship(
        "Activity",
        primaryjoin="and_(Customer.id == foreign(Activity.entity_id), Activity.entity_type == 'CUSTOMER')",
        viewonly=True
    )
    ratings = relationship(
        "Rating",
        primaryjoin="and_(Customer.id == foreign(Rating.entity_id), Rating.entity_type == 'CUSTOMER')",
        viewonly=True
    )
    tags = relationship(
        "Tag",
        primaryjoin="and_(Customer.id == foreign(Tag.entity_id), Tag.entity_type == 'CUSTOMER')",
        viewonly=True
    )

    __mapper_args__ = {"polymorphic_identity": "customer"}

    def __repr__(self):
        display_name = self.business_name or f"{self.first_name} {self.last_name}"
        return f"<Customer(id={self.id}, code={self.customer_code}, name={display_name})>"

    @property
    def display_name(self) -> str:
        """Return business name for business customers, or person name for individuals"""
        if self.customer_type == CustomerType.BUSINESS and self.business_name:
            return self.business_name
        return super().display_name
    
    @property
    def overall_rating(self) -> float:
        """Calculate overall customer rating average from ratings table"""
        # This would typically be calculated via a database query in the service layer
        # For now, we'll return 0.0 as a placeholder
        return 0.0

    def add_activity(self, activity_type: ActivityType, subject: str, description: str = None, 
                    assigned_to: str = None, scheduled_date: DateTime = None) -> Activity:
        """Helper method to add activities to this customer"""
        activity = Activity(
            entity_type="CUSTOMER",
            entity_id=self.id,
            activity_type=activity_type,
            subject=subject,
            description=description,
            assigned_to=assigned_to or self.sales_rep_id,
            scheduled_date=scheduled_date,
            company_id=self.company_id
        )
        return activity

    def add_tag(self, tag_value: str, tag_category: TagCategory = None, tag_color: str = None) -> Tag:
        """Helper method to add tags to this customer"""
        tag = Tag(
            entity_type="CUSTOMER",
            entity_id=self.id,
            tag_category=tag_category,
            tag_value=tag_value,
            tag_color=tag_color,
            company_id=self.company_id
        )
        return tag


# -----------------------------
# Quote Model
# -----------------------------

class Quote(BaseModel):
    __tablename__ = "quotes"
    __table_args__ = (
        UniqueConstraint('quote_number', 'company_id', name='uq_quote_number_per_company'),
        {'schema': SCHEMA}
    )

    company_id = Column(UUID(as_uuid=True), ForeignKey("public.companies.id", ondelete="RESTRICT"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.customers.id", ondelete="RESTRICT"), nullable=False)
    
    quote_number = Column(String(50), nullable=False)
    quote_date = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=False)
    
    status = Column(Enum(QuoteStatus), default=QuoteStatus.DRAFT)
    
    # Financial totals
    subtotal = Column(Numeric(15, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), default=0)
    currency_id = Column(UUID(as_uuid=True), ForeignKey("public.currencies.id"))
    
    # Additional information
    notes = Column(Text)
    terms_and_conditions = Column(Text)
    
    # Tracking
    sent_date = Column(DateTime)
    viewed_date = Column(DateTime)
    accepted_date = Column(DateTime)
    
    # Relationships
    customer = relationship("Customer", back_populates="quotes")
    line_items = relationship("QuoteLineItem", back_populates="quote", cascade="all, delete-orphan")
    sales_order = relationship("SalesOrder", back_populates="quote", uselist=False)


# -----------------------------
# Quote Line Item Model
# -----------------------------

class QuoteLineItem(BaseModel):
    __tablename__ = "quote_line_items"
    __table_args__ = {'schema': SCHEMA}

    quote_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.quotes.id", ondelete="CASCADE"), nullable=False)
    line_number = Column(Integer, nullable=False)
    
    # Product/Service reference
    product_id = Column(UUID(as_uuid=True), nullable=True)  # Reference to shared Product model (to be created)
    product_code = Column(String(50))
    product_name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Quantities and pricing
    quantity = Column(Numeric(10, 3), nullable=False, default=1)
    unit_price = Column(Numeric(15, 2), nullable=False)
    discount_percentage = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    line_total = Column(Numeric(15, 2), nullable=False)
    
    # Tax information
    tax_code = Column(String(20))
    tax_rate = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    
    # Additional attributes
    attributes = Column(JSON)  # Flexible product attributes
    
    # Relationships
    quote = relationship("Quote", back_populates="line_items")


# -----------------------------
# Sales Order Model
# -----------------------------

class SalesOrder(BaseModel):
    __tablename__ = "sales_orders"
    __table_args__ = (
        UniqueConstraint('order_number', 'company_id', name='uq_order_number_per_company'),
        {'schema': SCHEMA}
    )

    company_id = Column(UUID(as_uuid=True), ForeignKey("public.companies.id", ondelete="RESTRICT"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.customers.id", ondelete="RESTRICT"), nullable=False)
    quote_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.quotes.id"), nullable=True)
    
    order_number = Column(String(50), nullable=False)
    order_date = Column(Date, nullable=False)
    expected_delivery_date = Column(Date)
    
    status = Column(Enum(OrderStatus), default=OrderStatus.DRAFT)
    
    # Financial totals
    subtotal = Column(Numeric(15, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    shipping_amount = Column(Numeric(15, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), default=0)
    currency_id = Column(UUID(as_uuid=True), ForeignKey("public.currencies.id"))
    
    # Shipping information
    shipping_address = Column(JSON)
    shipping_method = Column(String(100))
    tracking_number = Column(String(100))
    
    # Additional information
    notes = Column(Text)
    internal_notes = Column(Text)
    
    # Relationships
    customer = relationship("Customer", back_populates="orders")
    quote = relationship("Quote", back_populates="sales_order")
    line_items = relationship("SalesOrderLineItem", back_populates="sales_order", cascade="all, delete-orphan")
    invoices = relationship("SalesInvoice", back_populates="sales_order")


# -----------------------------
# Sales Order Line Item Model
# -----------------------------

class SalesOrderLineItem(BaseModel):
    __tablename__ = "sales_order_line_items"
    __table_args__ = {'schema': SCHEMA}

    sales_order_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.sales_orders.id", ondelete="CASCADE"), nullable=False)
    line_number = Column(Integer, nullable=False)
    
    # Product/Service reference
    product_id = Column(UUID(as_uuid=True), nullable=True)
    product_code = Column(String(50))
    product_name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Quantities and pricing
    quantity_ordered = Column(Numeric(10, 3), nullable=False)
    quantity_shipped = Column(Numeric(10, 3), default=0)
    quantity_invoiced = Column(Numeric(10, 3), default=0)
    unit_price = Column(Numeric(15, 2), nullable=False)
    discount_percentage = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    line_total = Column(Numeric(15, 2), nullable=False)
    
    # Tax information
    tax_code = Column(String(20))
    tax_rate = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    
    # Fulfillment
    expected_ship_date = Column(Date)
    actual_ship_date = Column(Date)
    
    # Additional attributes
    attributes = Column(JSON)
    
    # Relationships
    sales_order = relationship("SalesOrder", back_populates="line_items")


# -----------------------------
# Sales Invoice Model
# -----------------------------

class SalesInvoice(BaseModel):
    __tablename__ = "sales_invoices"
    __table_args__ = (
        UniqueConstraint('invoice_number', 'company_id', name='uq_invoice_number_per_company'),
        {'schema': SCHEMA}
    )

    company_id = Column(UUID(as_uuid=True), ForeignKey("public.companies.id", ondelete="RESTRICT"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.customers.id", ondelete="RESTRICT"), nullable=False)
    sales_order_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.sales_orders.id"), nullable=True)
    
    invoice_number = Column(String(50), nullable=False)
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    
    # Financial totals
    subtotal = Column(Numeric(15, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), default=0)
    paid_amount = Column(Numeric(15, 2), default=0)
    balance_due = Column(Numeric(15, 2), default=0)
    currency_id = Column(UUID(as_uuid=True), ForeignKey("public.currencies.id"))
    
    # Payment terms
    payment_terms = Column(Integer, default=30)  # Days
    late_fee_rate = Column(Numeric(5, 2), default=0)
    
    # Additional information
    notes = Column(Text)
    
    # Accounting integration
    accounting_journal_entry_id = Column(UUID(as_uuid=True), nullable=True)  # Link to accounting
    
    # Relationships
    customer = relationship("Customer", back_populates="invoices")
    sales_order = relationship("SalesOrder", back_populates="invoices")
    line_items = relationship("SalesInvoiceLineItem", back_populates="sales_invoice", cascade="all, delete-orphan")
    payments = relationship("CustomerPayment", back_populates="invoice")


# -----------------------------
# Sales Invoice Line Item Model
# -----------------------------

class SalesInvoiceLineItem(BaseModel):
    __tablename__ = "sales_invoice_line_items"
    __table_args__ = {'schema': SCHEMA}

    sales_invoice_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.sales_invoices.id", ondelete="CASCADE"), nullable=False)
    line_number = Column(Integer, nullable=False)
    
    # Product/Service reference
    product_id = Column(UUID(as_uuid=True), nullable=True)
    product_code = Column(String(50))
    product_name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Quantities and pricing
    quantity = Column(Numeric(10, 3), nullable=False)
    unit_price = Column(Numeric(15, 2), nullable=False)
    discount_percentage = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    line_total = Column(Numeric(15, 2), nullable=False)
    
    # Tax information
    tax_code = Column(String(20))
    tax_rate = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    
    # Accounting integration
    revenue_account_id = Column(UUID(as_uuid=True), nullable=True)  # Link to chart of accounts
    
    # Additional attributes
    attributes = Column(JSON)
    
    # Relationships
    sales_invoice = relationship("SalesInvoice", back_populates="line_items")


# -----------------------------
# Customer Payment Model
# -----------------------------

class CustomerPayment(BaseModel):
    __tablename__ = "customer_payments"
    __table_args__ = (
        UniqueConstraint('payment_reference', 'company_id', name='uq_payment_reference_per_company'),
        {'schema': SCHEMA}
    )

    company_id = Column(UUID(as_uuid=True), ForeignKey("public.companies.id", ondelete="RESTRICT"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.customers.id", ondelete="RESTRICT"), nullable=False)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.sales_invoices.id"), nullable=True)
    
    payment_reference = Column(String(50), nullable=False)
    payment_date = Column(Date, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency_id = Column(UUID(as_uuid=True), ForeignKey("public.currencies.id"))
    
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Payment details
    transaction_id = Column(String(100))  # External payment processor ID
    bank_reference = Column(String(100))
    notes = Column(Text)
    
    # Accounting integration
    accounting_journal_entry_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="payments")
    invoice = relationship("SalesInvoice", back_populates="payments")


# -----------------------------
# Sales Commission Model
# -----------------------------

class SalesCommission(BaseModel):
    __tablename__ = "sales_commissions"
    __table_args__ = {'schema': SCHEMA}

    sales_rep_id = Column(UUID(as_uuid=True), nullable=False)  # Link to HR employee
    sales_order_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.sales_orders.id"), nullable=True)
    sales_invoice_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.sales_invoices.id"), nullable=True)
    
    commission_rate = Column(Numeric(5, 2), nullable=False)  # Percentage
    commission_amount = Column(Numeric(15, 2), nullable=False)
    currency_id = Column(UUID(as_uuid=True), ForeignKey("public.currencies.id"))
    
    calculation_date = Column(Date, nullable=False)
    payment_date = Column(Date)
    is_paid = Column(Boolean, default=False)
    
    notes = Column(Text)


# -----------------------------
# Product Bundle Model (for bundled products/services)
# -----------------------------

class ProductBundle(BaseModel):
    __tablename__ = "product_bundles"
    __table_args__ = (
        UniqueConstraint('bundle_code', 'company_id', name='uq_bundle_code_per_company'),
        {'schema': SCHEMA}
    )

    company_id = Column(UUID(as_uuid=True), ForeignKey("public.companies.id", ondelete="RESTRICT"), nullable=False)
    bundle_code = Column(String(50), nullable=False)
    bundle_name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Pricing
    bundle_price = Column(Numeric(15, 2), nullable=False)
    currency_id = Column(UUID(as_uuid=True), ForeignKey("public.currencies.id"))
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relationships
    bundle_items = relationship("ProductBundleItem", back_populates="bundle", cascade="all, delete-orphan")


# -----------------------------
# Product Bundle Item Model
# -----------------------------

class ProductBundleItem(BaseModel):
    __tablename__ = "product_bundle_items"
    __table_args__ = {'schema': SCHEMA}

    bundle_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.product_bundles.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), nullable=False)  # Reference to shared Product model
    
    quantity = Column(Numeric(10, 3), nullable=False, default=1)
    unit_price = Column(Numeric(15, 2))  # Override price for bundle
    
    # Relationships
    bundle = relationship("ProductBundle", back_populates="bundle_items")


# -----------------------------
# Vendor Model (Inherits from Person)
# -----------------------------

class Vendor(Person):
    __tablename__ = "vendors"
    __table_args__ = (
        {'schema': SCHEMA}
    )

    id = Column(PG_UUID(as_uuid=True), ForeignKey("public.persons.id"), primary_key=True, default=uuid.uuid4)
    vendor_code = Column(String(50), nullable=False)
    
    # Business information
    business_name = Column(String(255), nullable=True)  # For business vendors
    industry = Column(String(100))
    vendor_type = Column(PGEnum(CustomerType, name="vendor_type_enum", create_type=False), 
                        default=CustomerType.BUSINESS, nullable=False)
    vendor_status = Column(PGEnum(CustomerStatus, name="vendor_status_enum", create_type=False),
                          default=CustomerStatus.ACTIVE, nullable=False)
    tax_id = Column(String(50))
    
    # Financial information
    credit_limit = Column(Numeric(15, 2), default=0)
    payment_terms = Column(Integer, default=30)  # Days
    currency_id = Column(UUID(as_uuid=True), ForeignKey("public.currencies.id"))
    
    # Vendor information
    procurement_rep_id = Column(UUID(as_uuid=True), ForeignKey("hr.employees.id"), nullable=True)
    vendor_since = Column(Date, nullable=True)
    last_purchase_date = Column(Date, nullable=True)
    total_purchases_value = Column(Numeric(15, 2), default=0)
    
    # Quality and performance
    quality_rating = Column(Numeric(3, 2), default=0)  # 0-5 rating
    delivery_rating = Column(Numeric(3, 2), default=0)  # 0-5 rating
    service_rating = Column(Numeric(3, 2), default=0)  # 0-5 rating
    
    # Add company_id column for multi-tenancy/ownership
    #company_id = Column(UUID(as_uuid=True), ForeignKey("public.companies.id", ondelete="SET NULL"), nullable=True)

    # Additional data
    tags = Column(JSON, nullable=True)
    custom_fields = Column(JSON, nullable=True)
    
    # Relationships
    procurement_rep = relationship("Employee", foreign_keys=[procurement_rep_id])
    
    # Unified relationships using entity_type/entity_id pattern
    activities = relationship(
        "Activity",
        primaryjoin="and_(Vendor.id == foreign(Activity.entity_id), Activity.entity_type == 'VENDOR')",
        viewonly=True
    )
    ratings = relationship(
        "Rating",
        primaryjoin="and_(Vendor.id == foreign(Rating.entity_id), Rating.entity_type == 'VENDOR')",
        viewonly=True
    )
    tags = relationship(
        "Tag",
        primaryjoin="and_(Vendor.id == foreign(Tag.entity_id), Tag.entity_type == 'VENDOR')",
        viewonly=True
    )
    
    __mapper_args__ = {"polymorphic_identity": "vendor"}

    def __repr__(self):
        display_name = self.business_name or f"{self.first_name} {self.last_name}"
        return f"<Vendor(id={self.id}, code={self.vendor_code}, name={display_name})>"

    @property
    def display_name(self) -> str:
        """Return business name for business vendors, or person name for individuals"""
        if self.vendor_type == CustomerType.BUSINESS and self.business_name:
            return self.business_name
        return super().display_name

    @property
    def average_rating(self) -> dict:
        """Get average ratings by type for this vendor"""
        # This would be calculated in the service layer
        return {
            'quality': float(self.quality_rating) if self.quality_rating else 0.0,
            'delivery': float(self.delivery_rating) if self.delivery_rating else 0.0,
            'service': float(self.service_rating) if self.service_rating else 0.0
        }

    def add_activity(self, activity_type: ActivityType, subject: str, description: str = None, 
                    assigned_to: str = None, scheduled_date: DateTime = None) -> Activity:
        """Helper method to add activities to this vendor"""
        activity = Activity(
            entity_type="VENDOR",
            entity_id=self.id,
            activity_type=activity_type,
            subject=subject,
            description=description,
            assigned_to=assigned_to or self.procurement_rep_id,
            scheduled_date=scheduled_date,
            company_id=self.company_id
        )
        return activity


# -----------------------------
# Lead Model (Inherits from Person)
# -----------------------------

class Lead(Person):
    __tablename__ = "leads"
    __table_args__ = (
        {'schema': SCHEMA}
    )

    id = Column(PG_UUID(as_uuid=True), ForeignKey("public.persons.id"), primary_key=True, default=uuid.uuid4)
    lead_code = Column(String(50), nullable=False)
    
    # Lead information
    source = Column(String(100))  # How did we get this lead
    lead_type = Column(PGEnum(CustomerType, name="lead_type_enum", create_type=False), 
                      default=CustomerType.INDIVIDUAL, nullable=False)
    lead_status = Column(String(50), default="NEW")  # NEW, CONTACTED, QUALIFIED, etc.
    
    # Business information (for business leads)
    business_name = Column(String(255), nullable=True)
    industry = Column(String(100))
    
    # Lead scoring and qualification
    lead_score = Column(Integer, default=0)
    qualification_status = Column(String(50), default="UNQUALIFIED")  # UNQUALIFIED, QUALIFIED, DISQUALIFIED
    
    # Sales process
    sales_rep_id = Column(UUID(as_uuid=True), ForeignKey("hr.employees.id"), nullable=True)
    converted_to_customer_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.customers.id"), nullable=True)
    conversion_date = Column(Date, nullable=True)
    
    # Tracking
    first_contact_date = Column(Date, nullable=True)
    last_contact_date = Column(Date, nullable=True)
    expected_close_date = Column(Date, nullable=True)
    estimated_value = Column(Numeric(15, 2), default=0)
    
    # Add company_id column for multi-tenancy/ownership
    #company_id = Column(UUID(as_uuid=True), ForeignKey("public.companies.id", ondelete="SET NULL"), nullable=True)

    # Additional data
    tags = Column(JSON, nullable=True)
    custom_fields = Column(JSON, nullable=True)
    lead_notes = Column(Text)  # Renamed from 'notes' to 'lead_notes' to avoid conflict
    
    # Relationships
    sales_rep = relationship("Employee", foreign_keys=[sales_rep_id])
    converted_customer = relationship("Customer", foreign_keys=[converted_to_customer_id])
    
    # Unified relationships using entity_type/entity_id pattern
    activities = relationship(
        "Activity",
        primaryjoin="and_(Lead.id == foreign(Activity.entity_id), Activity.entity_type == 'LEAD')",
        viewonly=True
    )
    ratings = relationship( 
        "Rating",
        primaryjoin="and_(Lead.id == foreign(Rating.entity_id), Rating.entity_type == 'LEAD')",
        viewonly=True
    )
    tags = relationship(
        "Tag",
        primaryjoin="and_(Lead.id == foreign(Tag.entity_id), Tag.entity_type == 'LEAD')",
        viewonly=True
    )
    
    __mapper_args__ = {"polymorphic_identity": "lead"}

    def __repr__(self):
        display_name = self.business_name or f"{self.first_name} {self.last_name}"
        return f"<Lead(id={self.id}, code={self.lead_code}, name={display_name})>"

    @property
    def display_name(self) -> str:
        """Return business name for business leads, or person name for individuals"""
        if self.lead_type == CustomerType.BUSINESS and self.business_name:
            return self.business_name
        return super().display_name

    def add_activity(self, activity_type: ActivityType, subject: str, description: str = None, 
                    assigned_to: str = None, scheduled_date: DateTime = None) -> Activity:
        """Helper method to add activities to this lead"""
        activity = Activity(
            entity_type="LEAD",
            entity_id=self.id,
            activity_type=activity_type,
            subject=subject,
            description=description,
            assigned_to=assigned_to or self.sales_rep_id,
            scheduled_date=scheduled_date,
            company_id=self.company_id
        )
        return activity

    def convert_to_customer(self, customer_code: str) -> 'Customer':
        """Convert this lead to a customer"""
        customer = Customer(
            id=self.id,  # Keep the same person ID
            customer_code=customer_code,
            business_name=self.business_name,
            industry=self.industry,
            customer_type=self.lead_type,
            customer_status=CustomerStatus.ACTIVE,
            sales_rep_id=self.sales_rep_id,
            customer_since=func.current_date(),
            company_id=self.company_id
        )
        
        # Update lead conversion tracking
        self.converted_to_customer_id = self.id
        self.conversion_date = func.current_date()
        
        return customer