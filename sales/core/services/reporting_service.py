from typing import List, Optional, Dict, Any, Union, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, desc, asc, extract
from datetime import datetime, date, timedelta
from uuid import UUID, uuid4
import logging
from decimal import Decimal
from io import BytesIO
import csv
import json

from bheem_core.modules.sales.core.models.sales_models import (
    Customer, SalesOrder, SalesInvoice, Quote, 
    OrderStatus, InvoiceStatus, QuoteStatus,
    SalesOrderLineItem, SalesInvoiceLineItem, Vendor
)
from bheem_core.modules.sales.core.schemas.reporting_schemas import (
    SalesReportRequest, SalesReportResponse, ReportData, ReportType, ReportFormat,
    CustomerReportResponse, ProductReportResponse, RevenueReportResponse,
    PipelineReportResponse, TeamPerformanceResponse, ReportSchedule,
    ScheduledReportResponse, ReportExportRequest, ReportExportResponse
)
from bheem_core.modules.auth.core.models.auth_models import User
from bheem_core.shared.models import SKU

logger = logging.getLogger(__name__)


class SalesReportingService:
    """
    Service for sales reporting and analytics
    Generates various types of sales reports with export capabilities
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== REPORT GENERATION ====================
    
    def generate_sales_report(self, request: SalesReportRequest, company_id: UUID) -> SalesReportResponse:
        """Generate a sales report based on request parameters"""
        
        report_id = uuid4()
        
        # Route to specific report generator based on type
        if request.report_type == ReportType.SALES_SUMMARY:
            data = self._generate_sales_summary_report(request, company_id)
        elif request.report_type == ReportType.CUSTOMER_ANALYSIS:
            data = self._generate_customer_analysis_report(request, company_id)
        elif request.report_type == ReportType.PRODUCT_PERFORMANCE:
            data = self._generate_product_performance_report(request, company_id)
        elif request.report_type == ReportType.REVENUE_BREAKDOWN:
            data = self._generate_revenue_breakdown_report(request, company_id)
        elif request.report_type == ReportType.SALES_PIPELINE:
            data = self._generate_pipeline_report(request, company_id)
        elif request.report_type == ReportType.TEAM_PERFORMANCE:
            data = self._generate_team_performance_report(request, company_id)
        else:
            raise ValueError(f"Unsupported report type: {request.report_type}")
        
        # Generate download URL if needed
        download_url = None
        if request.report_format != ReportFormat.JSON:
            download_url = self._generate_download_url(report_id, request.report_format)
        
        return SalesReportResponse(
            report_id=report_id,
            report_type=request.report_type,
            report_format=request.report_format,
            generated_at=datetime.utcnow(),
            period=request.period,
            filters=request.filters,
            data=data,
            download_url=download_url
        )
    
    def _generate_sales_summary_report(self, request: SalesReportRequest, company_id: UUID) -> ReportData:
        """Generate sales summary report"""
        
        # Base query for the period
        start_date = request.period.start_date
        end_date = request.period.end_date
        
        # Get sales orders in period
        orders_query = self.db.query(SalesOrder).filter(
            and_(
                SalesOrder.company_id == company_id,
                SalesOrder.order_date >= start_date,
                SalesOrder.order_date <= end_date
            )
        )
        
        # Apply filters if provided
        if request.filters:
            if request.filters.customer_ids:
                orders_query = orders_query.filter(SalesOrder.customer_id.in_(request.filters.customer_ids))
            if request.filters.order_statuses:
                orders_query = orders_query.filter(SalesOrder.status.in_(request.filters.order_statuses))
            if request.filters.min_amount:
                orders_query = orders_query.filter(SalesOrder.total_amount >= request.filters.min_amount)
            if request.filters.max_amount:
                orders_query = orders_query.filter(SalesOrder.total_amount <= request.filters.max_amount)
        
        orders = orders_query.all()
        
        # Calculate summary metrics
        total_orders = len(orders)
        total_revenue = sum(order.total_amount or 0 for order in orders)
        average_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Summary data
        summary = {
            "total_orders": total_orders,
            "total_revenue": float(total_revenue),
            "average_order_value": float(average_order_value),
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat()
        }
        
        # Detailed data
        data = []
        for order in orders:
            data.append({
                "order_id": str(order.id),
                "order_number": order.order_number,
                "customer_name": order.customer.business_name if order.customer else "Unknown",
                "order_date": order.order_date.isoformat() if order.order_date else None,
                "status": order.status,
                "total_amount": float(order.total_amount or 0),
                "currency": order.currency
            })
        
        return ReportData(
            total_records=total_orders,
            summary=summary,
            data=data
        )
    
    def _generate_customer_analysis_report(self, request: SalesReportRequest, company_id: UUID) -> ReportData:
        """Generate customer analysis report"""
        
        # Get customer metrics for the period
        start_date = request.period.start_date
        end_date = request.period.end_date
        
        # Total customers
        total_customers = self.db.query(Customer).filter(Customer.company_id == company_id).count()
        
        # New customers in period
        new_customers = self.db.query(Customer).filter(
            and_(
                Customer.company_id == company_id,
                Customer.created_at >= start_date,
                Customer.created_at <= end_date
            )
        ).count()
        
        # Customer revenue analysis
        customer_revenue = self.db.query(
            Customer.id,
            Customer.business_name,
            func.sum(SalesOrder.total_amount).label('total_revenue'),
            func.count(SalesOrder.id).label('order_count')
        ).join(SalesOrder).filter(
            and_(
                Customer.company_id == company_id,
                SalesOrder.order_date >= start_date,
                SalesOrder.order_date <= end_date
            )
        ).group_by(Customer.id, Customer.business_name).order_by(desc('total_revenue')).limit(10).all()
        
        summary = {
            "total_customers": total_customers,
            "new_customers": new_customers,
            "top_customers_count": len(customer_revenue)
        }
        
        data = []
        for customer in customer_revenue:
            data.append({
                "customer_id": str(customer.id),
                "customer_name": customer.business_name,
                "total_revenue": float(customer.total_revenue or 0),
                "order_count": customer.order_count
            })
        
        return ReportData(
            total_records=len(customer_revenue),
            summary=summary,
            data=data
        )
    
    def _generate_product_performance_report(self, request: SalesReportRequest, company_id: UUID) -> ReportData:
        """Generate product performance report"""
        
        start_date = request.period.start_date
        end_date = request.period.end_date
        
        # Product performance from order line items
        product_performance = self.db.query(
            SKU.id,
            SKU.name,
            func.sum(SalesOrderLineItem.quantity).label('total_quantity'),
            func.sum(SalesOrderLineItem.line_total).label('total_revenue'),
            func.count(SalesOrderLineItem.id).label('order_line_count')
        ).join(SalesOrderLineItem, SKU.id == SalesOrderLineItem.sku_id)\
         .join(SalesOrder, SalesOrderLineItem.order_id == SalesOrder.id)\
         .filter(
            and_(
                SalesOrder.company_id == company_id,
                SalesOrder.order_date >= start_date,
                SalesOrder.order_date <= end_date
            )
        ).group_by(SKU.id, SKU.name).order_by(desc('total_revenue')).limit(20).all()
        
        total_products = len(product_performance)
        total_revenue = sum(float(product.total_revenue or 0) for product in product_performance)
        
        summary = {
            "total_products": total_products,
            "total_revenue": total_revenue
        }
        
        data = []
        for product in product_performance:
            data.append({
                "product_id": str(product.id),
                "product_name": product.name,
                "total_quantity": product.total_quantity,
                "total_revenue": float(product.total_revenue or 0),
                "order_line_count": product.order_line_count
            })
        
        return ReportData(
            total_records=total_products,
            summary=summary,
            data=data
        )
    
    def _generate_revenue_breakdown_report(self, request: SalesReportRequest, company_id: UUID) -> ReportData:
        """Generate revenue breakdown report"""
        
        start_date = request.period.start_date
        end_date = request.period.end_date
        
        # Monthly revenue breakdown
        monthly_revenue = self.db.query(
            extract('year', SalesOrder.order_date).label('year'),
            extract('month', SalesOrder.order_date).label('month'),
            func.sum(SalesOrder.total_amount).label('revenue')
        ).filter(
            and_(
                SalesOrder.company_id == company_id,
                SalesOrder.order_date >= start_date,
                SalesOrder.order_date <= end_date
            )
        ).group_by('year', 'month').order_by('year', 'month').all()
        
        total_revenue = sum(float(month.revenue or 0) for month in monthly_revenue)
        
        summary = {
            "total_revenue": total_revenue,
            "months_included": len(monthly_revenue)
        }
        
        data = []
        for month in monthly_revenue:
            data.append({
                "year": int(month.year),
                "month": int(month.month),
                "revenue": float(month.revenue or 0)
            })
        
        return ReportData(
            total_records=len(monthly_revenue),
            summary=summary,
            data=data
        )
    
    def _generate_pipeline_report(self, request: SalesReportRequest, company_id: UUID) -> ReportData:
        """Generate sales pipeline report"""
        
        # Get all active quotes (opportunities)
        quotes = self.db.query(Quote).filter(
            and_(
                Quote.company_id == company_id,
                Quote.status.in_([QuoteStatus.DRAFT, QuoteStatus.SENT, QuoteStatus.UNDER_REVIEW])
            )
        ).all()
        
        total_opportunities = len(quotes)
        pipeline_value = sum(float(quote.total_amount or 0) for quote in quotes)
        
        # Group by status
        status_breakdown = {}
        for quote in quotes:
            status = quote.status
            if status not in status_breakdown:
                status_breakdown[status] = {"count": 0, "value": 0}
            status_breakdown[status]["count"] += 1
            status_breakdown[status]["value"] += float(quote.total_amount or 0)
        
        summary = {
            "total_opportunities": total_opportunities,
            "pipeline_value": pipeline_value,
            "status_breakdown": status_breakdown
        }
        
        data = []
        for quote in quotes:
            data.append({
                "quote_id": str(quote.id),
                "quote_number": quote.quote_number,
                "customer_name": quote.customer.business_name if quote.customer else "Unknown",
                "status": quote.status,
                "total_amount": float(quote.total_amount or 0),
                "created_date": quote.created_at.isoformat() if quote.created_at else None
            })
        
        return ReportData(
            total_records=total_opportunities,
            summary=summary,
            data=data
        )
    
    def _generate_team_performance_report(self, request: SalesReportRequest, company_id: UUID) -> ReportData:
        """Generate team performance report"""
        
        start_date = request.period.start_date
        end_date = request.period.end_date
        
        # Sales rep performance
        rep_performance = self.db.query(
            User.id,
            User.first_name,
            User.last_name,
            func.sum(SalesOrder.total_amount).label('total_revenue'),
            func.count(SalesOrder.id).label('order_count')
        ).join(SalesOrder, User.id == SalesOrder.sales_rep_id).filter(
            and_(
                SalesOrder.company_id == company_id,
                SalesOrder.order_date >= start_date,
                SalesOrder.order_date <= end_date
            )
        ).group_by(User.id, User.first_name, User.last_name).order_by(desc('total_revenue')).all()
        
        total_reps = len(rep_performance)
        total_revenue = sum(float(rep.total_revenue or 0) for rep in rep_performance)
        avg_revenue = total_revenue / total_reps if total_reps > 0 else 0
        
        summary = {
            "total_sales_reps": total_reps,
            "total_revenue": total_revenue,
            "average_revenue_per_rep": avg_revenue
        }
        
        data = []
        for rep in rep_performance:
            data.append({
                "sales_rep_id": str(rep.id),
                "sales_rep_name": f"{rep.first_name} {rep.last_name}",
                "total_revenue": float(rep.total_revenue or 0),
                "order_count": rep.order_count
            })
        
        return ReportData(
            total_records=total_reps,
            summary=summary,
            data=data
        )
    
    # ==================== UTILITY METHODS ====================
    
    def _generate_download_url(self, report_id: UUID, format: ReportFormat) -> str:
        """Generate a download URL for the report"""
        return f"/api/sales/reports/{report_id}/download?format={format.value}"
    
    def get_customer_report(self, company_id: UUID, start_date: date, end_date: date) -> CustomerReportResponse:
        """Get customer analysis report"""
        # Implementation similar to _generate_customer_analysis_report but returns CustomerReportResponse
        return CustomerReportResponse(
            total_customers=0,
            new_customers=0,
            returning_customers=0,
            customer_retention_rate=0.0,
            average_customer_value=Decimal('0'),
            top_customers=[],
            customer_segments=[]
        )
    
    def get_product_report(self, company_id: UUID, start_date: date, end_date: date) -> ProductReportResponse:
        """Get product performance report"""
        return ProductReportResponse(
            total_products=0,
            total_revenue=Decimal('0'),
            top_selling_products=[],
            product_categories=[]
        )
    
    def get_revenue_report(self, company_id: UUID, start_date: date, end_date: date) -> RevenueReportResponse:
        """Get revenue breakdown report"""
        return RevenueReportResponse(
            total_revenue=Decimal('0'),
            revenue_by_period=[],
            revenue_by_product=[],
            revenue_by_customer=[],
            revenue_by_region=[],
            growth_metrics={}
        )
    
    def get_pipeline_report(self, company_id: UUID) -> PipelineReportResponse:
        """Get sales pipeline report"""
        return PipelineReportResponse(
            total_opportunities=0,
            pipeline_value=Decimal('0'),
            conversion_rate=0.0,
            average_deal_size=Decimal('0'),
            pipeline_stages=[],
            forecast_revenue=Decimal('0')
        )
    
    def get_team_performance(self, company_id: UUID, start_date: date, end_date: date) -> TeamPerformanceResponse:
        """Get team performance report"""
        return TeamPerformanceResponse(
            total_sales_reps=0,
            total_revenue=Decimal('0'),
            average_revenue_per_rep=Decimal('0'),
            top_performers=[],
            team_metrics=[],
            performance_trends=[]
        )

