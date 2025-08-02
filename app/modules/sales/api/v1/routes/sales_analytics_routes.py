from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.modules.auth.core.services.permissions_service import (
    require_roles, require_api_permission, get_current_user_id, get_current_company_id
)
from app.shared.models import UserRole
from app.modules.sales.core.services.sales_analytics_service import SalesAnalyticsService
from app.modules.sales.core.schemas.sales_analytics_schemas import SalesDashboardResponse, SalesForecastResponse, SalesPerformanceResponse

router = APIRouter(prefix="/analytics", tags=["Sales Analytics"])

@router.get("/dashboard", 
            response_model=SalesDashboardResponse,
            dependencies=[
                Depends(lambda: require_api_permission("sales.analytics.dashboard")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
            ])
async def get_sales_dashboard(
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = SalesAnalyticsService(db)
    dashboard = service.get_dashboard()
    return dashboard

@router.get("/forecasts", 
            response_model=SalesForecastResponse,
            dependencies=[
                Depends(lambda: require_api_permission("sales.analytics.forecasts")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.VIEWER]))
            ])
async def get_sales_forecasts(
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = SalesAnalyticsService(db)
    forecasts = service.get_forecasts()
    return forecasts

@router.get("/performance", 
            response_model=SalesPerformanceResponse,
            dependencies=[
                Depends(lambda: require_api_permission("sales.analytics.performance")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.VIEWER]))
            ])
async def get_sales_performance(
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = SalesAnalyticsService(db)
    performance = service.get_performance()
    return performance

@router.get("/reporting", 
            response_model=SalesDashboardResponse,
            dependencies=[
                Depends(lambda: require_api_permission("sales.analytics.reporting")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.VIEWER]))
            ])
async def get_sales_reporting(
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = SalesAnalyticsService(db)
    report = service.get_reporting()
    return report
