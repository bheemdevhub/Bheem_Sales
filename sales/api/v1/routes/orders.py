from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from bheem_core.core.database import get_db
from bheem_core.modules.auth.core.services.permissions_service import (
    require_roles, require_api_permission, get_current_user_id, get_current_company_id
)
from bheem_core.shared.models import UserRole
from bheem_core.modules.sales.core.schemas.sales_order_schemas import (
    SalesOrderCreate, SalesOrderUpdate, SalesOrderResponse, SalesOrderPaginatedResponse
)
from bheem_core.modules.sales.core.services.sales_order_service import SalesOrderService

router = APIRouter(prefix="/orders", tags=["Order Management"])

@router.post("/", 
             response_model=SalesOrderResponse, 
             status_code=status.HTTP_201_CREATED,
             dependencies=[
                 Depends(lambda: require_api_permission("sales.orders.create")),
                 Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
             ])
async def create_order(
    order_data: SalesOrderCreate, 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    return SalesOrderService(db).create_order(order_data)

@router.get("/", 
            response_model=SalesOrderPaginatedResponse,
            dependencies=[
                Depends(lambda: require_api_permission("sales.orders.read")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
            ])
async def list_orders(
    db: Session = Depends(get_db),
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
    return SalesOrderService(db).list_orders(limit=limit, offset=offset, status=status, customer_id=customer_id)

@router.get("/{order_id}", 
            response_model=SalesOrderResponse,
            dependencies=[
                Depends(lambda: require_api_permission("sales.orders.read")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
            ])
async def get_order(
    order_id: UUID, 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    return SalesOrderService(db).get_order(order_id)

@router.put("/{order_id}", 
            response_model=SalesOrderResponse,
            dependencies=[
                Depends(lambda: require_api_permission("sales.orders.update")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
            ])
async def update_order(
    order_id: UUID, 
    order_data: SalesOrderUpdate, 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    return SalesOrderService(db).update_order(order_id, order_data)

@router.post("/{order_id}/ship", 
             response_model=SalesOrderResponse,
             dependencies=[
                 Depends(lambda: require_api_permission("sales.orders.ship")),
                 Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
             ])
async def ship_order(
    order_id: UUID, 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    return SalesOrderService(db).ship_order(order_id)

@router.post("/{order_id}/cancel", 
             response_model=SalesOrderResponse,
             dependencies=[
                 Depends(lambda: require_api_permission("sales.orders.cancel")),
                 Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
             ])
async def cancel_order(
    order_id: UUID, 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    return SalesOrderService(db).cancel_order(order_id)

