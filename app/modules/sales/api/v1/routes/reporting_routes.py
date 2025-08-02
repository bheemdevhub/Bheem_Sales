from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from app.core.database import get_db
from app.modules.auth.core.services.permissions_service import (
    require_roles, require_api_permission, get_current_user_id, get_current_company_id
)
from app.shared.models import UserRole
from app.modules.sales.core.schemas.reporting_schemas import (
    SalesReportCreate, SalesReportResponse, SalesReportFilter,
    SalesDashboardResponse, SalesMetricsResponse, SalesKPIResponse,
    SalesForecastResponse, SalesPerformanceResponse, SalesCommissionResponse,
    SalesLeaderboardResponse, SalesActivitySummaryResponse
)
from app.modules.sales.core.services.reporting_service import SalesReportingService

router = APIRouter(prefix="/reports", tags=["Sales Reports"])

# ==================== SALES DASHBOARD ====================

@router.get("/dashboard", response_model=SalesDashboardResponse,
         dependencies=[
             Depends(lambda: require_api_permission("sales.dashboard.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
         ])
async def get_sales_dashboard(
    date_range: Optional[str] = Query("last_30_days", description="today|yesterday|last_7_days|last_30_days|last_90_days|this_month|last_month|this_quarter|last_quarter|this_year|last_year|custom"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    user_id: Optional[UUID] = Query(None),
    team_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get sales dashboard data"""
    service = SalesReportingService(db)
    return service.get_dashboard(
        company_id, 
        date_range, 
        start_date, 
        end_date, 
        user_id or current_user_id,
        team_id
    )

@router.get("/metrics", response_model=SalesMetricsResponse,
         dependencies=[
             Depends(lambda: require_api_permission("sales.metrics.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
         ])
async def get_sales_metrics(
    period: str = Query("monthly", description="daily|weekly|monthly|quarterly|yearly"),
    user_id: Optional[UUID] = Query(None),
    team_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get sales metrics"""
    service = SalesReportingService(db)
    return service.get_metrics(
        company_id,
        period,
        user_id or current_user_id,
        team_id
    )

@router.get("/kpis", response_model=SalesKPIResponse,
         dependencies=[
             Depends(lambda: require_api_permission("sales.kpi.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
         ])
async def get_sales_kpis(
    date_range: Optional[str] = Query("last_30_days"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    user_id: Optional[UUID] = Query(None),
    team_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get sales KPIs"""
    service = SalesReportingService(db)
    return service.get_kpis(
        company_id,
        date_range,
        start_date,
        end_date,
        user_id or current_user_id,
        team_id
    )

# ==================== SALES FORECASTING ====================

@router.get("/forecast", response_model=SalesForecastResponse,
         dependencies=[
             Depends(lambda: require_api_permission("sales.forecast.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.VIEWER]))
         ])
async def get_sales_forecast(
    forecast_period: str = Query("next_quarter", description="next_month|next_quarter|next_year"),
    user_id: Optional[UUID] = Query(None),
    team_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get sales forecast"""
    service = SalesReportingService(db)
    return service.get_forecast(
        company_id,
        forecast_period,
        user_id or current_user_id,
        team_id
    )

@router.get("/performance", response_model=SalesPerformanceResponse,
         dependencies=[
             Depends(lambda: require_api_permission("sales.performance.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
         ])
async def get_sales_performance(
    period: str = Query("monthly", description="daily|weekly|monthly|quarterly|yearly"),
    user_id: Optional[UUID] = Query(None),
    team_id: Optional[UUID] = Query(None),
    include_comparison: bool = Query(True),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get sales performance report"""
    service = SalesReportingService(db)
    return service.get_performance(
        company_id,
        period,
        user_id or current_user_id,
        team_id,
        include_comparison
    )

# ==================== SALES COMMISSIONS ====================

@router.get("/commissions", response_model=SalesCommissionResponse,
         dependencies=[
             Depends(lambda: require_api_permission("sales.commission.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
         ])
async def get_sales_commissions(
    period: str = Query("this_month", description="this_month|last_month|this_quarter|last_quarter|this_year|custom"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    user_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None, description="pending|approved|paid"),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get sales commissions"""
    service = SalesReportingService(db)
    return service.get_commissions(
        company_id,
        period,
        start_date,
        end_date,
        user_id or current_user_id,
        status
    )

@router.post("/commissions/calculate", response_model=dict,
          dependencies=[
              Depends(lambda: require_api_permission("sales.commission.calculate")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
          ])
async def calculate_sales_commissions(
    period: str = Body(..., description="this_month|last_month|this_quarter|last_quarter|this_year|custom"),
    start_date: Optional[date] = Body(None),
    end_date: Optional[date] = Body(None),
    user_ids: Optional[List[UUID]] = Body(None),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Calculate sales commissions"""
    service = SalesReportingService(db)
    return service.calculate_commissions(
        company_id,
        period,
        start_date,
        end_date,
        user_ids,
        current_user_id
    )

# ==================== SALES LEADERBOARD ====================

@router.get("/leaderboard", response_model=SalesLeaderboardResponse,
         dependencies=[
             Depends(lambda: require_api_permission("sales.leaderboard.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
         ])
async def get_sales_leaderboard(
    metric: str = Query("revenue", description="revenue|deals_closed|activities|calls|emails|meetings"),
    period: str = Query("this_month", description="this_week|this_month|this_quarter|this_year"),
    team_id: Optional[UUID] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get sales leaderboard"""
    service = SalesReportingService(db)
    return service.get_leaderboard(
        company_id,
        metric,
        period,
        team_id,
        limit
    )

# ==================== CUSTOM REPORTS ====================

@router.post("/custom", response_model=SalesReportResponse, status_code=status.HTTP_201_CREATED,
          dependencies=[
              Depends(lambda: require_api_permission("sales.report.create")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
          ])
async def create_custom_report(
    report_data: SalesReportCreate,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Create custom sales report"""
    service = SalesReportingService(db)
    return service.create_custom_report(report_data, current_user_id, company_id)

@router.get("/custom", response_model=List[SalesReportResponse],
         dependencies=[
             Depends(lambda: require_api_permission("sales.report.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
         ])
async def list_custom_reports(
    created_by: Optional[UUID] = Query(None),
    report_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """List custom sales reports"""
    service = SalesReportingService(db)
    return service.list_custom_reports(
        company_id,
        created_by or current_user_id,
        report_type
    )

@router.get("/custom/{report_id}", response_model=SalesReportResponse,
         dependencies=[
             Depends(lambda: require_api_permission("sales.report.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
         ])
async def get_custom_report(
    report_id: UUID = Path(...),
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get custom sales report"""
    service = SalesReportingService(db)
    return service.get_custom_report(report_id, company_id)

@router.post("/custom/{report_id}/generate", response_model=dict,
          dependencies=[
              Depends(lambda: require_api_permission("sales.report.generate")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
          ])
async def generate_custom_report(
    report_id: UUID = Path(...),
    filters: Optional[SalesReportFilter] = Body(None),
    export_format: str = Query("json", description="json|csv|pdf|xlsx"),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Generate custom sales report"""
    service = SalesReportingService(db)
    return service.generate_custom_report(
        report_id,
        filters,
        export_format,
        current_user_id,
        company_id
    )

# ==================== ACTIVITY REPORTS ====================

@router.get("/activities", response_model=SalesActivitySummaryResponse,
         dependencies=[
             Depends(lambda: require_api_permission("sales.activity.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
         ])
async def get_activity_summary(
    date_range: Optional[str] = Query("last_30_days"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    user_id: Optional[UUID] = Query(None),
    team_id: Optional[UUID] = Query(None),
    activity_type: Optional[str] = Query(None, description="call|email|meeting|task|note"),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get sales activity summary"""
    service = SalesReportingService(db)
    return service.get_activity_summary(
        company_id,
        date_range,
        start_date,
        end_date,
        user_id or current_user_id,
        team_id,
        activity_type
    )

# ==================== EXPORT REPORTS ====================

@router.post("/export", response_model=dict,
          dependencies=[
              Depends(lambda: require_api_permission("sales.report.export")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
          ])
async def export_sales_report(
    report_type: str = Body(..., description="dashboard|metrics|kpis|forecast|performance|commissions|leaderboard|activities"),
    format: str = Body("csv", description="csv|pdf|xlsx"),
    filters: Optional[Dict[str, Any]] = Body(None),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Export sales report"""
    service = SalesReportingService(db)
    return service.export_report(
        report_type,
        format,
        filters,
        current_user_id,
        company_id
    )

# ==================== SCHEDULED REPORTS ====================

@router.post("/schedule", response_model=dict, status_code=status.HTTP_201_CREATED,
          dependencies=[
              Depends(lambda: require_api_permission("sales.report.schedule")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
          ])
async def schedule_sales_report(
    report_type: str = Body(...),
    schedule: str = Body(..., description="daily|weekly|monthly|quarterly"),
    recipients: List[str] = Body(...),
    filters: Optional[Dict[str, Any]] = Body(None),
    format: str = Body("pdf", description="pdf|csv|xlsx"),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Schedule sales report"""
    service = SalesReportingService(db)
    return service.schedule_report(
        report_type,
        schedule,
        recipients,
        filters,
        format,
        current_user_id,
        company_id
    )

@router.get("/scheduled", response_model=List[dict],
         dependencies=[
             Depends(lambda: require_api_permission("sales.report.schedule.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
         ])
async def list_scheduled_reports(
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """List scheduled sales reports"""
    service = SalesReportingService(db)
    return service.list_scheduled_reports(current_user_id, company_id)

@router.delete("/scheduled/{schedule_id}", response_model=dict,
            dependencies=[
                Depends(lambda: require_api_permission("sales.report.schedule.delete")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
            ])
async def cancel_scheduled_report(
    schedule_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Cancel scheduled sales report"""
    service = SalesReportingService(db)
    return service.cancel_scheduled_report(schedule_id, current_user_id, company_id)
