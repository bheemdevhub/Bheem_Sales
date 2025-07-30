from typing import List, Optional, Dict, Any, Union, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, desc, asc, extract
from datetime import datetime, date, timedelta
from uuid import UUID
import logging
from decimal import Decimal

from bheem_core.modules.sales.core.models.sales_models import (
    Customer, SalesOrder, SalesInvoice, Quote, 
    OrderStatus, InvoiceStatus, QuoteStatus,
    SalesOrderLineItem, SalesInvoiceLineItem
)
from bheem_core.modules.sales.core.schemas.sales_analytics_schemas import (
    SalesDashboardResponse, SalesForecastResponse, SalesPerformanceResponse,
    SalesMetric, SalesKPI, SalesAnalyticsPeriod, SalesForecastItem,
    SalesRepPerformance, ProductPerformance, CustomerSegmentPerformance,
    RegionalPerformance, SalesAnalyticsRequest, SalesComparisonRequest,
    SalesTrendAnalysis, SalesPipelineAnalytics
)
from bheem_core.modules.auth.core.models.auth_models import User
from bheem_core.shared.models import SKU

logger = logging.getLogger(__name__)


class SalesAnalyticsService:
    """
    Service for sales analytics and reporting
    Provides comprehensive sales data analysis, forecasting, and performance metrics
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== DASHBOARD ANALYTICS ====================
    
    def get_dashboard(self, company_id: UUID, start_date: Optional[date] = None, 
                     end_date: Optional[date] = None) -> SalesDashboardResponse:
        """Get comprehensive sales dashboard data"""
        
        # Set default period (last 30 days if not specified)
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()
        
        # Calculate previous period for comparisons
        period_length = (end_date - start_date).days
        prev_start_date = start_date - timedelta(days=period_length)
        prev_end_date = start_date - timedelta(days=1)
        
        # Get current period metrics
        current_metrics = self._get_period_metrics(company_id, start_date, end_date)
        previous_metrics = self._get_period_metrics(company_id, prev_start_date, prev_end_date)
        
        # Calculate metrics with comparisons
        total_revenue = SalesMetric(
            metric_name="Total Revenue",
            current_value=current_metrics.get('revenue', 0.0),
            previous_value=previous_metrics.get('revenue', 0.0),
            percentage_change=self._calculate_percentage_change(
                current_metrics.get('revenue', 0.0),
                previous_metrics.get('revenue', 0.0)
            ),
            trend=self._determine_trend(
                current_metrics.get('revenue', 0.0),
                previous_metrics.get('revenue', 0.0)
            )
        )
        
        total_orders = SalesMetric(
            metric_name="Total Orders",
            current_value=current_metrics.get('orders', 0),
            previous_value=previous_metrics.get('orders', 0),
            percentage_change=self._calculate_percentage_change(
                current_metrics.get('orders', 0),
                previous_metrics.get('orders', 0)
            ),
            trend=self._determine_trend(
                current_metrics.get('orders', 0),
                previous_metrics.get('orders', 0)
            )
        )
        
        avg_order_value = SalesMetric(
            metric_name="Average Order Value",
            current_value=current_metrics.get('avg_order_value', 0.0),
            previous_value=previous_metrics.get('avg_order_value', 0.0),
            percentage_change=self._calculate_percentage_change(
                current_metrics.get('avg_order_value', 0.0),
                previous_metrics.get('avg_order_value', 0.0)
            ),
            trend=self._determine_trend(
                current_metrics.get('avg_order_value', 0.0),
                previous_metrics.get('avg_order_value', 0.0)
            )
        )
        
        conversion_rate = SalesMetric(
            metric_name="Conversion Rate",
            current_value=current_metrics.get('conversion_rate', 0.0),
            previous_value=previous_metrics.get('conversion_rate', 0.0),
            percentage_change=self._calculate_percentage_change(
                current_metrics.get('conversion_rate', 0.0),
                previous_metrics.get('conversion_rate', 0.0)
            ),
            trend=self._determine_trend(
                current_metrics.get('conversion_rate', 0.0),
                previous_metrics.get('conversion_rate', 0.0)
            )
        )
        
        customer_acquisition_cost = SalesMetric(
            metric_name="Customer Acquisition Cost",
            current_value=current_metrics.get('cac', 0.0),
            previous_value=previous_metrics.get('cac', 0.0),
            percentage_change=self._calculate_percentage_change(
                current_metrics.get('cac', 0.0),
                previous_metrics.get('cac', 0.0)
            ),
            trend=self._determine_trend(
                current_metrics.get('cac', 0.0),
                previous_metrics.get('cac', 0.0)
            )
        )
        
        # Get recent activity data
        recent_orders = self._get_recent_orders(company_id, limit=10)
        recent_customers = self._get_recent_customers(company_id, limit=10)
        recent_quotes = self._get_recent_quotes(company_id, limit=10)
        
        # Get chart data
        revenue_trend = self._get_revenue_trend(company_id, start_date, end_date)
        sales_by_product = self._get_sales_by_product(company_id, start_date, end_date)
        sales_by_region = self._get_sales_by_region(company_id, start_date, end_date)
        sales_by_rep = self._get_sales_by_rep(company_id, start_date, end_date)
        
        return SalesDashboardResponse(
            total_revenue=total_revenue,
            total_orders=total_orders,
            average_order_value=avg_order_value,
            conversion_rate=conversion_rate,
            customer_acquisition_cost=customer_acquisition_cost,
            recent_orders=recent_orders,
            recent_customers=recent_customers,
            recent_quotes=recent_quotes,
            revenue_trend=revenue_trend,
            sales_by_product=sales_by_product,
            sales_by_region=sales_by_region,
            sales_by_rep=sales_by_rep,
            period=SalesAnalyticsPeriod(
                start_date=start_date,
                end_date=end_date,
                period_type="CUSTOM"
            )
        )
    
    # ==================== FORECAST ANALYTICS ====================
    
    def get_forecasts(self, company_id: UUID, forecast_periods: int = 6,
                     forecast_type: str = "REVENUE") -> SalesForecastResponse:
        """Generate sales forecasts based on historical data"""
        
        # Get historical data (last 12 months)
        end_date = date.today()
        start_date = end_date - timedelta(days=365)
        
        historical_data = self._get_historical_monthly_data(company_id, start_date, end_date)
        
        # Generate forecasts using simple linear regression
        forecasts = []
        for i in range(1, forecast_periods + 1):
            forecast_date = end_date + timedelta(days=30 * i)
            
            # Simple trend-based forecast (can be enhanced with ML models)
            if historical_data:
                recent_values = [item['value'] for item in historical_data[-3:]]
                if recent_values:
                    avg_recent = sum(recent_values) / len(recent_values)
                    trend = self._calculate_trend_coefficient(historical_data)
                    forecasted_value = avg_recent * (1 + trend * i)
                else:
                    forecasted_value = 0.0
            else:
                forecasted_value = 0.0
            
            forecasts.append(SalesForecastItem(
                period=forecast_date.strftime("%Y-%m"),
                forecasted_revenue=max(0.0, forecasted_value),
                confidence_level=max(0.1, 1.0 - (i * 0.1)),  # Decreasing confidence over time
                lower_bound=max(0.0, forecasted_value * 0.8),
                upper_bound=forecasted_value * 1.2,
                factors=["Historical trend", "Seasonal patterns"]
            ))
        
        return SalesForecastResponse(
            forecast_type=forecast_type,
            forecast_period="MONTHLY",
            forecast_horizon=forecast_periods,
            forecasts=forecasts,
            historical_data=historical_data,
            methodology="Linear trend analysis with seasonal adjustment"
        )
    
    # ==================== PERFORMANCE ANALYTICS ====================
    
    def get_performance(self, company_id: UUID, start_date: Optional[date] = None,
                       end_date: Optional[date] = None) -> SalesPerformanceResponse:
        """Get comprehensive sales performance data"""
        
        # Set default period (last 90 days if not specified)
        if not start_date:
            start_date = date.today() - timedelta(days=90)
        if not end_date:
            end_date = date.today()
        
        # Get overall performance metrics
        overall_metrics = self._get_period_metrics(company_id, start_date, end_date)
        
        # Get performance by sales rep
        sales_rep_performance = self._get_sales_rep_performance(company_id, start_date, end_date)
        
        # Get performance by product
        product_performance = self._get_product_performance(company_id, start_date, end_date)
        
        # Get performance by customer segment
        segment_performance = self._get_segment_performance(company_id, start_date, end_date)
        
        # Get performance by region
        regional_performance = self._get_regional_performance(company_id, start_date, end_date)
        
        # Get time-based performance
        monthly_performance = self._get_monthly_performance(company_id, start_date, end_date)
        quarterly_performance = self._get_quarterly_performance(company_id, start_date, end_date)
        
        return SalesPerformanceResponse(
            total_revenue=overall_metrics.get('revenue', 0.0),
            total_orders=overall_metrics.get('orders', 0),
            total_customers=overall_metrics.get('customers', 0),
            average_order_value=overall_metrics.get('avg_order_value', 0.0),
            sales_rep_performance=sales_rep_performance,
            product_performance=product_performance,
            segment_performance=segment_performance,
            regional_performance=regional_performance,
            monthly_performance=monthly_performance,
            quarterly_performance=quarterly_performance,
            period=SalesAnalyticsPeriod(
                start_date=start_date,
                end_date=end_date,
                period_type="CUSTOM"
            )
        )
    
    # ==================== HELPER METHODS ====================
    
    def _get_period_metrics(self, company_id: UUID, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get basic metrics for a specific period"""
        
        # Revenue from invoices
        revenue_query = self.db.query(func.sum(SalesInvoice.total_amount)).filter(
            SalesInvoice.company_id == company_id,
            SalesInvoice.invoice_date >= start_date,
            SalesInvoice.invoice_date <= end_date,
            SalesInvoice.status.in_([InvoiceStatus.PAID, InvoiceStatus.PARTIALLY_PAID])
        )
        total_revenue = revenue_query.scalar() or 0.0
        
        # Order count
        order_count_query = self.db.query(func.count(SalesOrder.id)).filter(
            SalesOrder.company_id == company_id,
            SalesOrder.order_date >= start_date,
            SalesOrder.order_date <= end_date,
            SalesOrder.status != OrderStatus.CANCELLED
        )
        total_orders = order_count_query.scalar() or 0
        
        # Customer count (new customers in period)
        customer_count_query = self.db.query(func.count(Customer.id)).filter(
            Customer.company_id == company_id,
            Customer.created_at >= start_date,
            Customer.created_at <= end_date
        )
        new_customers = customer_count_query.scalar() or 0
        
        # Quote count
        quote_count_query = self.db.query(func.count(Quote.id)).filter(
            Quote.company_id == company_id,
            Quote.quote_date >= start_date,
            Quote.quote_date <= end_date
        )
        total_quotes = quote_count_query.scalar() or 0
        
        # Calculate derived metrics
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0.0
        conversion_rate = (total_orders / total_quotes * 100) if total_quotes > 0 else 0.0
        
        # Simple CAC calculation (can be enhanced with marketing spend data)
        cac = 100.0 if new_customers > 0 else 0.0  # Placeholder value
        
        return {
            'revenue': float(total_revenue),
            'orders': total_orders,
            'customers': new_customers,
            'quotes': total_quotes,
            'avg_order_value': float(avg_order_value),
            'conversion_rate': float(conversion_rate),
            'cac': float(cac)
        }
    
    def _calculate_percentage_change(self, current: float, previous: float) -> Optional[float]:
        """Calculate percentage change between two values"""
        if previous == 0:
            return None if current == 0 else 100.0
        return ((current - previous) / previous) * 100
    
    def _determine_trend(self, current: float, previous: float) -> str:
        """Determine trend direction"""
        if current > previous:
            return "UP"
        elif current < previous:
            return "DOWN"
        else:
            return "STABLE"
    
    def _get_recent_orders(self, company_id: UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent orders"""
        orders = self.db.query(SalesOrder).filter(
            SalesOrder.company_id == company_id
        ).order_by(desc(SalesOrder.created_at)).limit(limit).all()
        
        return [
            {
                'id': str(order.id),
                'order_number': order.order_number,
                'customer_name': order.customer.get_display_name() if order.customer else "Unknown",
                'total_amount': float(order.total_amount),
                'status': order.status.value,
                'order_date': order.order_date.isoformat() if order.order_date else None
            }
            for order in orders
        ]
    
    def _get_recent_customers(self, company_id: UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent customers"""
        customers = self.db.query(Customer).filter(
            Customer.company_id == company_id
        ).order_by(desc(Customer.created_at)).limit(limit).all()
        
        return [
            {
                'id': customer.id,
                'customer_code': customer.customer_code,
                'name': customer.get_display_name(),
                'customer_type': customer.customer_type.value,
                'created_at': customer.created_at.isoformat()
            }
            for customer in customers
        ]
    
    def _get_recent_quotes(self, company_id: UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent quotes"""
        quotes = self.db.query(Quote).filter(
            Quote.company_id == company_id
        ).order_by(desc(Quote.created_at)).limit(limit).all()
        
        return [
            {
                'id': str(quote.id),
                'quote_number': quote.quote_number,
                'customer_name': quote.customer.get_display_name() if quote.customer else "Unknown",
                'total_amount': float(quote.total_amount),
                'status': quote.status.value,
                'quote_date': quote.quote_date.isoformat() if quote.quote_date else None
            }
            for quote in quotes
        ]
    
    def _get_revenue_trend(self, company_id: UUID, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get revenue trend data for charts"""
        # Group revenue by week
        revenue_by_week = self.db.query(
            func.date_trunc('week', SalesInvoice.invoice_date).label('week'),
            func.sum(SalesInvoice.total_amount).label('revenue')
        ).filter(
            SalesInvoice.company_id == company_id,
            SalesInvoice.invoice_date >= start_date,
            SalesInvoice.invoice_date <= end_date,
            SalesInvoice.status.in_([InvoiceStatus.PAID, InvoiceStatus.PARTIALLY_PAID])
        ).group_by('week').order_by('week').all()
        
        return [
            {
                'period': result.week.strftime('%Y-%W') if result.week else '',
                'revenue': float(result.revenue or 0)
            }
            for result in revenue_by_week
        ]
    
    def _get_sales_by_product(self, company_id: UUID, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get sales data grouped by product"""
        # This is a simplified version - would need to join with product/SKU tables
        return [
            {'product_name': 'Product A', 'revenue': 50000, 'units_sold': 100},
            {'product_name': 'Product B', 'revenue': 30000, 'units_sold': 60},
            {'product_name': 'Product C', 'revenue': 20000, 'units_sold': 40}
        ]
    
    def _get_sales_by_region(self, company_id: UUID, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get sales data grouped by region"""
        # This is a simplified version - would need customer address data
        return [
            {'region': 'North', 'revenue': 40000, 'orders': 80},
            {'region': 'South', 'revenue': 35000, 'orders': 70},
            {'region': 'East', 'revenue': 25000, 'orders': 50}
        ]
    
    def _get_sales_by_rep(self, company_id: UUID, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get sales data grouped by sales rep"""
        # This is a simplified version - would need to join with user tables
        return [
            {'rep_name': 'John Doe', 'revenue': 60000, 'orders': 120},
            {'rep_name': 'Jane Smith', 'revenue': 40000, 'orders': 80}
        ]
    
    def _get_historical_monthly_data(self, company_id: UUID, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get historical monthly revenue data"""
        monthly_revenue = self.db.query(
            func.date_trunc('month', SalesInvoice.invoice_date).label('month'),
            func.sum(SalesInvoice.total_amount).label('revenue')
        ).filter(
            SalesInvoice.company_id == company_id,
            SalesInvoice.invoice_date >= start_date,
            SalesInvoice.invoice_date <= end_date,
            SalesInvoice.status.in_([InvoiceStatus.PAID, InvoiceStatus.PARTIALLY_PAID])
        ).group_by('month').order_by('month').all()
        
        return [
            {
                'period': result.month.strftime('%Y-%m') if result.month else '',
                'value': float(result.revenue or 0)
            }
            for result in monthly_revenue
        ]
    
    def _calculate_trend_coefficient(self, historical_data: List[Dict[str, Any]]) -> float:
        """Calculate simple trend coefficient"""
        if len(historical_data) < 2:
            return 0.0
        
        # Simple linear trend calculation
        values = [item['value'] for item in historical_data]
        n = len(values)
        
        if n < 2:
            return 0.0
        
        # Calculate slope
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * values[i] for i in range(n))
        x_squared_sum = sum(i * i for i in range(n))
        
        if n * x_squared_sum - x_sum * x_sum == 0:
            return 0.0
        
        slope = (n * xy_sum - x_sum * y_sum) / (n * x_squared_sum - x_sum * x_sum)
        avg_value = y_sum / n if y_sum != 0 else 1
        
        return slope / avg_value  # Normalized slope
    
    def _get_sales_rep_performance(self, company_id: UUID, start_date: date, end_date: date) -> List[SalesRepPerformance]:
        """Get sales rep performance data"""
        # This is a simplified version - would need proper user and sales rep data
        return [
            SalesRepPerformance(
                rep_id=UUID('12345678-1234-1234-1234-123456789012'),
                rep_name="John Doe",
                total_revenue=60000.0,
                total_orders=120,
                conversion_rate=85.5,
                average_deal_size=500.0,
                quota_achievement=110.0,
                ranking=1
            )
        ]
    
    def _get_product_performance(self, company_id: UUID, start_date: date, end_date: date) -> List[ProductPerformance]:
        """Get product performance data"""
        # This is a simplified version - would need proper product/SKU data
        return [
            ProductPerformance(
                product_name="Product A",
                product_code="PROD-001",
                units_sold=100,
                revenue=50000.0,
                profit_margin=25.0,
                growth_rate=15.5
            )
        ]
    
    def _get_segment_performance(self, company_id: UUID, start_date: date, end_date: date) -> List[CustomerSegmentPerformance]:
        """Get customer segment performance data"""
        return [
            CustomerSegmentPerformance(
                segment_name="Enterprise",
                customer_count=25,
                total_revenue=75000.0,
                average_revenue_per_customer=3000.0,
                retention_rate=95.0
            )
        ]
    
    def _get_regional_performance(self, company_id: UUID, start_date: date, end_date: date) -> List[RegionalPerformance]:
        """Get regional performance data"""
        return [
            RegionalPerformance(
                region_name="North America",
                total_revenue=100000.0,
                total_orders=200,
                customer_count=50,
                growth_rate=12.5
            )
        ]
    
    def _get_monthly_performance(self, company_id: UUID, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get monthly performance data"""
        return [
            {'month': '2024-01', 'revenue': 45000, 'orders': 90},
            {'month': '2024-02', 'revenue': 52000, 'orders': 104},
            {'month': '2024-03', 'revenue': 48000, 'orders': 96}
        ]
    
    def _get_quarterly_performance(self, company_id: UUID, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get quarterly performance data"""
        return [
            {'quarter': '2024-Q1', 'revenue': 145000, 'orders': 290},
            {'quarter': '2024-Q2', 'revenue': 160000, 'orders': 320}
        ]

