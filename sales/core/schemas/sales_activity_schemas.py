from typing import Optional, List, Dict, Any, Union
from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, Field, validator
from bheem_core.shared.models import ActivityType, ActivityStatus


# Base Schema for Sales Activities
class SalesActivityBase(BaseModel):
    entity_type: str = Field(..., description="Type of entity this activity is related to: CUSTOMER, LEAD, VENDOR, QUOTE, etc.")
    entity_id: str = Field(..., description="ID of the entity this activity is related to")
    activity_type: ActivityType
    subject: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    assigned_to: Optional[UUID] = None
    scheduled_date: Optional[datetime] = None
    due_date: Optional[date] = None
    status: ActivityStatus = ActivityStatus.PENDING
    is_completed: bool = False
    completion_date: Optional[datetime] = None
    notes: Optional[str] = None
    priority: Optional[str] = "MEDIUM"  # LOW, MEDIUM, HIGH
    
    @validator('entity_type')
    def validate_entity_type(cls, v):
        valid_types = ["CUSTOMER", "LEAD", "VENDOR", "QUOTE", "SALES_ORDER", "INVOICE", "PAYMENT", "OPPORTUNITY"]
        if v not in valid_types:
            raise ValueError(f"Entity type must be one of {valid_types}")
        return v


# Create Schema for Sales Activities
class SalesActivityCreate(SalesActivityBase):
    company_id: UUID


# Update Schema for Sales Activities
class SalesActivityUpdate(BaseModel):
    activity_type: Optional[ActivityType] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[UUID] = None
    scheduled_date: Optional[datetime] = None
    due_date: Optional[date] = None
    status: Optional[ActivityStatus] = None
    is_completed: Optional[bool] = None
    completion_date: Optional[datetime] = None
    notes: Optional[str] = None
    priority: Optional[str] = None


# Response Schema for Sales Activities
class SalesActivityResponse(SalesActivityBase):
    id: UUID
    company_id: UUID
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


# Detail Response Schema for Sales Activities with Related Data
class SalesActivityDetailResponse(SalesActivityResponse):
    entity_name: Optional[str] = None
    assigned_to_name: Optional[str] = None
    created_by_name: Optional[str] = None
    related_activities: List[Dict[str, Any]] = []


# Complete Activity Schema
class SalesActivityCompletion(BaseModel):
    completion_date: Optional[datetime] = None
    notes: Optional[str] = None
    outcome: Optional[str] = None


# Search Parameters for Sales Activities
class SalesActivitySearchParams(BaseModel):
    query: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    activity_type: Optional[ActivityType] = None
    status: Optional[ActivityStatus] = None
    assigned_to: Optional[UUID] = None
    is_completed: Optional[bool] = None
    scheduled_after: Optional[datetime] = None
    scheduled_before: Optional[datetime] = None
    due_after: Optional[date] = None
    due_before: Optional[date] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    priority: Optional[str] = None
    sort_by: Optional[str] = "scheduled_date"
    sort_desc: Optional[bool] = False
    limit: Optional[int] = 100
    offset: Optional[int] = 0


# Paginated Response for Sales Activities
class SalesActivityPaginatedResponse(BaseModel):
    items: List[SalesActivityResponse]
    total: int
    limit: int
    offset: int
    hasMore: bool


# Sales Dashboard KPI Schema
class SalesDashboardKPI(BaseModel):
    period: str
    total_sales: float = 0.0
    new_customers: int = 0
    orders_count: int = 0
    average_order_value: float = 0.0
    invoices_count: int = 0
    invoiced_amount: float = 0.0
    payments_received: float = 0.0
    total_outstanding: float = 0.0
    quotes_sent: int = 0
    quotes_accepted: int = 0
    quote_conversion_rate: float = 0.0
    leads_count: int = 0
    leads_converted: int = 0
    lead_conversion_rate: float = 0.0
    top_products: List[Dict[str, Any]] = []
    top_customers: List[Dict[str, Any]] = []


# Sales Analytics Request Schema
class SalesAnalyticsRequest(BaseModel):
    start_date: date
    end_date: date
    group_by: str = "month"  # day, week, month, quarter, year
    metrics: List[str] = ["sales", "orders", "customers"]
    customer_id: Optional[str] = None
    product_id: Optional[UUID] = None
    sales_rep_id: Optional[UUID] = None
    include_product_breakdown: bool = False
    include_customer_breakdown: bool = False
    include_forecast: bool = False


# Sales Report Schema
class SalesReportSchema(BaseModel):
    report_type: str  # sales_summary, customer_analysis, product_performance, etc.
    title: str
    description: Optional[str] = None
    start_date: date
    end_date: date
    generated_at: datetime = Field(default_factory=datetime.now)
    parameters: Dict[str, Any] = {}
    data: Dict[str, Any] = {}


# Upcoming Activities Summary
class UpcomingActivitiesSummary(BaseModel):
    overdue: int = 0
    today: int = 0
    this_week: int = 0
    next_week: int = 0
    future: int = 0
    activities: List[SalesActivityResponse] = []

