from typing import Optional, List, Dict, Any, Union
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field


# Base Analytics Schemas
class SalesMetric(BaseModel):
    """Base sales metric schema"""
    metric_name: str
    current_value: float
    previous_value: Optional[float] = None
    percentage_change: Optional[float] = None
    trend: Optional[str] = None  # UP, DOWN, STABLE


class SalesKPI(BaseModel):
    """Sales Key Performance Indicator"""
    kpi_name: str
    current_value: float
    target_value: Optional[float] = None
    achievement_percentage: Optional[float] = None
    period: str  # DAILY, WEEKLY, MONTHLY, QUARTERLY, YEARLY


class SalesAnalyticsPeriod(BaseModel):
    """Time period for analytics"""
    start_date: date
    end_date: date
    period_type: str  # DAY, WEEK, MONTH, QUARTER, YEAR


# Dashboard Response Schema
class SalesDashboardResponse(BaseModel):
    """Comprehensive sales dashboard data"""
    # Key Metrics
    total_revenue: SalesMetric
    total_orders: SalesMetric
    average_order_value: SalesMetric
    conversion_rate: SalesMetric
    customer_acquisition_cost: SalesMetric
    
    # KPIs
    monthly_recurring_revenue: Optional[SalesKPI] = None
    customer_lifetime_value: Optional[SalesKPI] = None
    sales_growth_rate: Optional[SalesKPI] = None
    
    # Recent Activity
    recent_orders: List[Dict[str, Any]] = []
    recent_customers: List[Dict[str, Any]] = []
    recent_quotes: List[Dict[str, Any]] = []
    
    # Charts Data
    revenue_trend: List[Dict[str, Any]] = []
    sales_by_product: List[Dict[str, Any]] = []
    sales_by_region: List[Dict[str, Any]] = []
    sales_by_rep: List[Dict[str, Any]] = []
    
    # Period Information
    period: SalesAnalyticsPeriod
    generated_at: datetime = Field(default_factory=datetime.now)


# Forecast Response Schema
class SalesForecastItem(BaseModel):
    """Individual forecast item"""
    period: str
    forecasted_revenue: float
    confidence_level: float  # 0.0 to 1.0
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    factors: Optional[List[str]] = None


class SalesForecastResponse(BaseModel):
    """Sales forecast data"""
    forecast_type: str  # REVENUE, UNITS, CUSTOMERS
    forecast_period: str  # MONTHLY, QUARTERLY, YEARLY
    forecast_horizon: int  # Number of periods ahead
    
    forecasts: List[SalesForecastItem]
    
    # Historical Data for Comparison
    historical_data: List[Dict[str, Any]] = []
    
    # Forecast Accuracy Metrics
    accuracy_metrics: Optional[Dict[str, float]] = None
    
    # Methodology Information
    methodology: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.now)


# Performance Response Schema
class SalesRepPerformance(BaseModel):
    """Individual sales rep performance"""
    rep_id: UUID
    rep_name: str
    total_revenue: float
    total_orders: int
    conversion_rate: float
    average_deal_size: float
    quota_achievement: Optional[float] = None
    ranking: Optional[int] = None


class ProductPerformance(BaseModel):
    """Product sales performance"""
    product_id: Optional[UUID] = None
    product_name: str
    product_code: Optional[str] = None
    units_sold: int
    revenue: float
    profit_margin: Optional[float] = None
    growth_rate: Optional[float] = None


class CustomerSegmentPerformance(BaseModel):
    """Customer segment performance"""
    segment_name: str
    customer_count: int
    total_revenue: float
    average_revenue_per_customer: float
    retention_rate: Optional[float] = None


class RegionalPerformance(BaseModel):
    """Regional sales performance"""
    region_name: str
    total_revenue: float
    total_orders: int
    customer_count: int
    growth_rate: Optional[float] = None


class SalesPerformanceResponse(BaseModel):
    """Comprehensive sales performance data"""
    # Overall Performance Summary
    total_revenue: float
    total_orders: int
    total_customers: int
    average_order_value: float
    
    # Performance by Sales Rep
    sales_rep_performance: List[SalesRepPerformance] = []
    
    # Performance by Product
    product_performance: List[ProductPerformance] = []
    
    # Performance by Customer Segment
    segment_performance: List[CustomerSegmentPerformance] = []
    
    # Performance by Region
    regional_performance: List[RegionalPerformance] = []
    
    # Time-based Performance
    monthly_performance: List[Dict[str, Any]] = []
    quarterly_performance: List[Dict[str, Any]] = []
    
    # Period Information
    period: SalesAnalyticsPeriod
    generated_at: datetime = Field(default_factory=datetime.now)


# Analytics Request Schemas
class SalesAnalyticsRequest(BaseModel):
    """Request parameters for sales analytics"""
    start_date: date
    end_date: date
    company_id: UUID
    include_forecasts: bool = True
    include_performance: bool = True
    group_by: Optional[str] = None  # PRODUCT, REGION, REP, CUSTOMER
    metrics: Optional[List[str]] = None  # Specific metrics to include


class SalesComparisonRequest(BaseModel):
    """Request for sales comparison analytics"""
    current_period_start: date
    current_period_end: date
    comparison_period_start: date
    comparison_period_end: date
    company_id: UUID
    comparison_type: str = "PERIOD"  # PERIOD, YEAR_OVER_YEAR


class SalesReportRequest(BaseModel):
    """Request for detailed sales reports"""
    report_type: str  # SUMMARY, DETAILED, CUSTOM
    period: SalesAnalyticsPeriod
    company_id: UUID
    filters: Optional[Dict[str, Any]] = None
    export_format: Optional[str] = "JSON"  # JSON, CSV, PDF


# Additional Analytics Schemas
class SalesTrendAnalysis(BaseModel):
    """Sales trend analysis"""
    trend_type: str  # REVENUE, ORDERS, CUSTOMERS
    trend_direction: str  # UP, DOWN, STABLE
    trend_strength: float  # 0.0 to 1.0
    correlation_factors: List[str] = []
    recommendations: List[str] = []


class SalesAnomalyDetection(BaseModel):
    """Sales anomaly detection"""
    anomaly_type: str  # SPIKE, DROP, PATTERN_BREAK
    detected_at: datetime
    severity: str  # LOW, MEDIUM, HIGH
    description: str
    affected_metrics: List[str] = []
    suggested_actions: List[str] = []


class SalesPipelineAnalytics(BaseModel):
    """Sales pipeline analytics"""
    total_pipeline_value: float
    weighted_pipeline_value: float
    average_deal_size: float
    average_sales_cycle: int  # days
    conversion_rate_by_stage: Dict[str, float] = {}
    pipeline_velocity: float
    stage_distribution: Dict[str, int] = {}


class SalesGoalTracking(BaseModel):
    """Sales goal tracking"""
    goal_id: UUID
    goal_name: str
    target_value: float
    current_value: float
    achievement_percentage: float
    remaining_period: int  # days
    projected_completion: Optional[date] = None
    on_track: bool

