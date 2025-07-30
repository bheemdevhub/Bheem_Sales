from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from uuid import UUID

from bheem_core.core.database import get_db
from bheem_core.modules.auth.core.services.permissions_service import (
    require_roles, require_api_permission, get_current_user_id, get_current_company_id
)
from bheem_core.shared.models import UserRole

# Import all route modules
from bheem_core.modules.sales.api.v1.routes.customer_routes import router as customer_router
from bheem_core.modules.sales.api.v1.routes.lead_routes import router as lead_router
from bheem_core.modules.sales.api.v1.routes.quote_routes import router as quote_router
from bheem_core.modules.sales.api.v1.routes.orders import router as orders_router
from bheem_core.modules.sales.api.v1.routes.invoices import router as invoices_router
from bheem_core.modules.sales.api.v1.routes.customer_payment_routes import router as payment_router
from bheem_core.modules.sales.api.v1.routes.sales_activity_routes import router as activity_router
from bheem_core.modules.sales.api.v1.routes.sales_analytics_routes import router as analytics_router
from bheem_core.modules.sales.api.v1.routes.vendor_routes import router as vendor_router
from bheem_core.modules.sales.api.v1.routes.bulk_operations_routes import router as bulk_router
from bheem_core.modules.sales.api.v1.routes.crm_routes import router as crm_router
from bheem_core.modules.sales.api.v1.routes.integration_routes import router as integration_router
from bheem_core.modules.sales.api.v1.routes.automation_routes import router as automation_router
from bheem_core.modules.sales.api.v1.routes.reporting_routes import router as reporting_router

# Import advanced business routes (with mock dependencies for now)
try:
    from bheem_core.modules.sales.api.v1.routes.advanced_business_routes import router as advanced_business_router
    from bheem_core.modules.sales.api.v1.routes.enhanced_dashboard_routes import router as enhanced_dashboard_router
except ImportError:
    advanced_business_router = None
    enhanced_dashboard_router = None

# Import custom SKU routes
try:
    from bheem_core.modules.sku.api.v1.routes.custom_sku_routes import router as custom_sku_router
except ImportError:
    custom_sku_router = None
    # Create mock routers if imports fail
    from fastapi import APIRouter
    advanced_business_router = APIRouter(prefix="/advanced-business", tags=["Advanced Business Features"])
    enhanced_dashboard_router = APIRouter(prefix="/enhanced-dashboard", tags=["Enhanced Dashboard"])

# Main sales router (no prefix, no tags)
# router = APIRouter()

router = APIRouter(
    tags=["Sales Module"]
)

# ==================== SALES MODULE DASHBOARD ====================

@router.get("/dashboard", 
            dependencies=[
                Depends(lambda: require_api_permission("sales.dashboard.read")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
            ])
async def sales_dashboard(
    db = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get comprehensive sales dashboard"""
    return {
        "user_id": str(current_user_id),
        "company_id": str(company_id),
        "dashboard_data": {
            "total_customers": 150,
            "active_leads": 45,
            "quotes_pending": 12,
            "orders_today": 8,
            "revenue_mtd": 125000.50,
            "recent_activities": []
        }
    }

@router.get("/module-info",
            dependencies=[
                Depends(lambda: require_api_permission("sales.info.read")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.VIEWER]))
            ])
async def get_module_info():
    """Get sales module information"""
    return {
        "module": "Sales",
        "version": "1.0.0",
        "description": "Comprehensive sales management system",
        "features": {
            "core": [
                "Customer Management",
                "Lead Management",
                "Quote Management", 
                "Order Management",
                "Invoice Management",
                "Payment Processing"
            ],
            "advanced": [
                "Sales Analytics",
                "Sales Automation",
                "Bulk Operations",
                "CRM Integration",
                "External Integrations",
                "Advanced Reporting"
            ]
        },
        "total_endpoints": 100,
        "authentication": "JWT with Role-based Access Control"
    }

# ==================== INCLUDE ALL ROUTE MODULES ====================

# Core Sales APIs
router.include_router(customer_router, tags=["Customer Management"])
router.include_router(lead_router, tags=["Lead Management"])
router.include_router(quote_router, tags=["Quote Management"])
router.include_router(orders_router, tags=["Order Management"])
router.include_router(invoices_router, tags=["Invoice Management"])
router.include_router(payment_router, tags=["Customer Payments"])
router.include_router(activity_router, tags=["Sales Activities"])
router.include_router(vendor_router, tags=["Vendor Management"])

# Analytics and Reporting
router.include_router(analytics_router, tags=["Sales Analytics"])
router.include_router(reporting_router, tags=["Sales Reports"])

# Advanced Features
router.include_router(bulk_router, tags=["Bulk Operations"])
router.include_router(crm_router, tags=["CRM Management"])
router.include_router(integration_router, tags=["External Integrations"])
router.include_router(automation_router, tags=["Sales Automation"])

# Advanced business features (with error handling)
try:
    from bheem_core.modules.sales.api.v1.routes.advanced_business_routes import router as advanced_business_router
    router.include_router(advanced_business_router, tags=["Advanced Business Features"])
except ImportError:
    pass

try:
    from bheem_core.modules.sales.api.v1.routes.enhanced_dashboard_routes import router as enhanced_dashboard_router
    router.include_router(enhanced_dashboard_router, tags=["Enhanced Dashboard"])
except ImportError:
    pass

# Custom SKU Management
if custom_sku_router:
    router.include_router(custom_sku_router, prefix="/custom-sku", tags=["Custom SKU Management"])
