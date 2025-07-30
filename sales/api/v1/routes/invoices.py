from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from bheem_core.core.database import get_db
from bheem_core.modules.auth.core.services.permissions_service import (
    require_roles, require_api_permission, get_current_user_id, get_current_company_id
)
from bheem_core.shared.models import UserRole
from bheem_core.modules.sales.core.schemas.sales_invoice_schemas import (
    SalesInvoiceCreate, SalesInvoiceUpdate, SalesInvoiceResponse, SalesInvoicePaginatedResponse
)
from bheem_core.modules.sales.core.services.sales_invoice_service import SalesInvoiceService

router = APIRouter(prefix="/invoices", tags=["Invoice Management"])

@router.post("/", 
             response_model=SalesInvoiceResponse, 
             status_code=status.HTTP_201_CREATED,
             dependencies=[
                 Depends(lambda: require_api_permission("sales.invoices.create")),
                 Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
             ])
async def create_invoice(
    invoice_data: SalesInvoiceCreate, 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    return SalesInvoiceService(db).create_invoice(invoice_data)

@router.get("/", 
            response_model=SalesInvoicePaginatedResponse,
            dependencies=[
                Depends(lambda: require_api_permission("sales.invoices.read")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
            ])
async def list_invoices(
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Records to skip"),
    status: Optional[str] = Query(None, description="Filter by invoice status"),
    customer_id: Optional[UUID] = Query(None, description="Filter by customer ID")
):
    """
    List invoices with optional filtering and pagination.
    """
    return SalesInvoiceService(db).list_invoices(limit=limit, offset=offset, status=status, customer_id=customer_id)

@router.get("/{invoice_id}", 
            response_model=SalesInvoiceResponse,
            dependencies=[
                Depends(lambda: require_api_permission("sales.invoices.read")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
            ])
async def get_invoice(
    invoice_id: UUID, 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    return SalesInvoiceService(db).get_invoice(invoice_id)

@router.post("/{invoice_id}/send", 
             response_model=SalesInvoiceResponse,
             dependencies=[
                 Depends(lambda: require_api_permission("sales.invoices.send")),
                 Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
             ])
async def send_invoice(
    invoice_id: UUID, 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    return SalesInvoiceService(db).send_invoice(invoice_id)

@router.post("/{invoice_id}/void", 
             response_model=SalesInvoiceResponse,
             dependencies=[
                 Depends(lambda: require_api_permission("sales.invoices.void")),
                 Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
             ])
async def void_invoice(
    invoice_id: UUID, 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    return SalesInvoiceService(db).void_invoice(invoice_id)

