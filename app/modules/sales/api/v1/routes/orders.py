from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from app.core.database import  get_db
from app.modules.auth.core.services.permissions_service import (
    require_roles, require_api_permission, get_current_user_id, get_current_company_id
)
from app.shared.models import UserRole
from app.modules.sales.core.schemas.sales_order_schemas import (
    SalesOrderCreate, SalesOrderUpdate, SalesOrderResponse, SalesOrderPaginatedResponse
)
from app.modules.sales.core.services.sales_order_service import SalesOrderService

router = APIRouter(prefix="/orders", tags=["Order Management"])

@router.post(
    "/",
    response_model=SalesOrderResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(lambda: require_api_permission("sales.orders.create")),
        Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
    ]
)
async def create_sales_order(
    order_data: SalesOrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = SalesOrderService(db)
    return await service.create_sales_order(order_data, current_user_id, company_id)

@router.get("/", 
            response_model=SalesOrderPaginatedResponse,
            dependencies=[
                Depends(lambda: require_api_permission("sales.orders.read")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
            ])
async def list_orders(
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Records to skip"),
    status: Optional[str] = Query(None, description="Filter by order status"),
    customer_id: Optional[UUID] = Query(None, description="Filter by customer ID")
):
    """
    List orders with optional filtering and pagination.
    """
    return await SalesOrderService(db).list_sales_orders(limit=limit, offset=offset, status=status, customer_id=customer_id)

@router.get("/{order_id}", 
            response_model=SalesOrderResponse,
            dependencies=[
                Depends(lambda: require_api_permission("sales.orders.read")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
            ])
async def get_order(
    order_id: UUID, 
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    return await SalesOrderService(db).get_sales_order_by_id(order_id)

@router.put("/{order_id}", 
            response_model=SalesOrderResponse,
            dependencies=[
                Depends(lambda: require_api_permission("sales.orders.update")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
            ])
async def update_order(
    order_id: UUID, 
    order_data: SalesOrderUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    return await SalesOrderService(db).update_sales_order(order_id, order_data)

@router.post("/{order_id}/ship", 
             response_model=SalesOrderResponse,
             dependencies=[
                 Depends(lambda: require_api_permission("sales.orders.ship")),
                 Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
             ])
async def ship_order(
    order_id: UUID, 
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    return await SalesOrderService(db).update_sales_order_status(order_id, "shipped")

@router.post("/{order_id}/cancel", 
             response_model=SalesOrderResponse,
             dependencies=[
                 Depends(lambda: require_api_permission("sales.orders.cancel")),
                 Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
             ])
async def cancel_order(
    order_id: UUID, 
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    return await SalesOrderService(db).update_sales_order_status(order_id, "cancelled")
