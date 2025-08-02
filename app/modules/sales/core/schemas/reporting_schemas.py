from typing import Optional, List, Dict, Any, Union
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field
from enum import Enum


class ReportType(str, Enum):
    """Available report types"""
    SALES_SUMMARY = "sales_summary"
    CUSTOMER_ANALYSIS = "customer_analysis"
    PRODUCT_PERFORMANCE = "product_performance"
    REVENUE_BREAKDOWN = "revenue_breakdown"
    SALES_PIPELINE = "sales_pipeline"
    TEAM_PERFORMANCE = "team_performance"


class ReportFormat(str, Enum):
    """Report output formats"""
    JSON = "json"
    PDF = "pdf"
    CSV = "csv"
    EXCEL = "excel"


class ReportPeriod(BaseModel):
    """Time period for reports"""
    start_date: date
    end_date: date
    period_type: Optional[str] = None  # DAILY, WEEKLY, MONTHLY, QUARTERLY, YEARLY


class ReportFilters(BaseModel):
    """Common filters for reports"""
    customer_ids: Optional[List[UUID]] = None
    sku_ids: Optional[List[UUID]] = None
    sales_rep_ids: Optional[List[UUID]] = None
    regions: Optional[List[str]] = None
    order_statuses: Optional[List[str]] = None
    invoice_statuses: Optional[List[str]] = None
    quote_statuses: Optional[List[str]] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None


# Alias for compatibility
SalesReportFilter = ReportFilters


class SalesReportRequest(BaseModel):
    """Request schema for sales reports"""
    report_type: ReportType
    report_format: ReportFormat = ReportFormat.JSON
    period: ReportPeriod
    filters: Optional[ReportFilters] = None
    include_details: bool = False
    group_by: Optional[List[str]] = None


# Alias for compatibility
SalesReportCreate = SalesReportRequest


class ReportData(BaseModel):
    """Base report data structure"""
    total_records: int
    summary: Dict[str, Any]
    data: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None


class SalesReportResponse(BaseModel):
    """Response schema for sales reports"""
    report_id: UUID
    report_type: ReportType
    report_format: ReportFormat
    generated_at: datetime
    period: ReportPeriod
    filters: Optional[ReportFilters] = None
    data: ReportData
    download_url: Optional[str] = None


class SalesDashboardResponse(BaseModel):
    """Sales dashboard response"""
    total_revenue: Decimal
    total_orders: int
    average_order_value: Decimal
    conversion_rate: float
    new_customers: int
    top_products: List[Dict[str, Any]]
    recent_activities: List[Dict[str, Any]]
    revenue_trend: List[Dict[str, Any]]


class SalesMetricsResponse(BaseModel):
    """Sales metrics response"""
    revenue_metrics: Dict[str, Any]
    order_metrics: Dict[str, Any]
    customer_metrics: Dict[str, Any]
    product_metrics: Dict[str, Any]
    period: ReportPeriod


class SalesKPIResponse(BaseModel):
    """Sales KPI response"""
    kpis: List[Dict[str, Any]]
    targets: List[Dict[str, Any]]
    achievements: List[Dict[str, Any]]
    period: ReportPeriod


class SalesForecastResponse(BaseModel):
    """Sales forecast response"""
    forecast_period: ReportPeriod
    predicted_revenue: Decimal
    confidence_level: float
    forecast_data: List[Dict[str, Any]]
    historical_data: List[Dict[str, Any]]


class SalesPerformanceResponse(BaseModel):
    """Sales performance response"""
    sales_reps: List[Dict[str, Any]]
    team_metrics: Dict[str, Any]
    individual_metrics: List[Dict[str, Any]]
    performance_trends: List[Dict[str, Any]]


class SalesCommissionResponse(BaseModel):
    """Sales commission response"""
    total_commission: Decimal
    commission_breakdown: List[Dict[str, Any]]
    payment_status: str
    period: ReportPeriod


class SalesLeaderboardResponse(BaseModel):
    """Sales leaderboard response"""
    top_performers: List[Dict[str, Any]]
    rankings: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    period: ReportPeriod


class SalesActivitySummaryResponse(BaseModel):
    """Sales activity summary response"""
    total_activities: int
    activities_by_type: Dict[str, int]
    recent_activities: List[Dict[str, Any]]
    completion_rates: Dict[str, float]


class CustomerReportResponse(BaseModel):
    """Customer analysis report response"""
    total_customers: int
    new_customers: int
    returning_customers: int
    customer_retention_rate: float
    average_customer_value: Decimal
    top_customers: List[Dict[str, Any]]
    customer_segments: List[Dict[str, Any]]


class ProductReportResponse(BaseModel):
    """Product performance report response"""
    total_products: int
    total_revenue: Decimal
    top_selling_products: List[Dict[str, Any]]
    product_categories: List[Dict[str, Any]]
    inventory_levels: Optional[List[Dict[str, Any]]] = None


class RevenueReportResponse(BaseModel):
    """Revenue breakdown report response"""
    total_revenue: Decimal
    revenue_by_period: List[Dict[str, Any]]
    revenue_by_product: List[Dict[str, Any]]
    revenue_by_customer: List[Dict[str, Any]]
    revenue_by_region: List[Dict[str, Any]]
    growth_metrics: Dict[str, Any]


class PipelineReportResponse(BaseModel):
    """Sales pipeline report response"""
    total_opportunities: int
    pipeline_value: Decimal
    conversion_rate: float
    average_deal_size: Decimal
    pipeline_stages: List[Dict[str, Any]]
    forecast_revenue: Decimal


class TeamPerformanceResponse(BaseModel):
    """Team performance report response"""
    total_sales_reps: int
    total_revenue: Decimal
    average_revenue_per_rep: Decimal
    top_performers: List[Dict[str, Any]]
    team_metrics: List[Dict[str, Any]]
    performance_trends: List[Dict[str, Any]]


class ReportSchedule(BaseModel):
    """Scheduled report configuration"""
    report_type: ReportType
    report_format: ReportFormat
    schedule_type: str  # DAILY, WEEKLY, MONTHLY
    recipients: List[str]  # Email addresses
    filters: Optional[ReportFilters] = None
    is_active: bool = True


class ScheduledReportResponse(BaseModel):
    """Scheduled report response"""
    schedule_id: UUID
    report_type: ReportType
    schedule_type: str
    next_run_date: datetime
    last_run_date: Optional[datetime] = None
    recipients: List[str]
    is_active: bool


class ReportExportRequest(BaseModel):
    """Request to export a report"""
    report_id: UUID
    export_format: ReportFormat
    include_charts: bool = False
    email_recipients: Optional[List[str]] = None


class ReportExportResponse(BaseModel):
    """Export response"""
    export_id: UUID
    download_url: str
    expires_at: datetime
    file_size: Optional[int] = None
