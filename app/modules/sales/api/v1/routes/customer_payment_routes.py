from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.modules.auth.core.services.permissions_service import (
    require_roles, require_api_permission, get_current_user_id, get_current_company_id
)
from app.shared.models import UserRole
from app.modules.sales.core.schemas.customer_payment_schemas import CustomerPaymentCreate, CustomerPaymentUpdate, CustomerPaymentResponse, CustomerPaymentPaginatedResponse
from app.modules.sales.core.services.customer_payment_service import CustomerPaymentService

router = APIRouter(prefix="/customer-payments", tags=["Customer Payments"])

@router.post(
    "/",
    response_model=CustomerPaymentResponse,
    dependencies=[
        Depends(lambda: require_api_permission("sales.payments.create")),
        Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
    ]
)
async def create_customer_payment(
    payment_data: CustomerPaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = CustomerPaymentService(db)
    payment = await service.create_payment(payment_data, current_user_id, company_id)
    return CustomerPaymentResponse.model_validate(payment, from_attributes=True)



@router.get("/", 
            response_model=CustomerPaymentPaginatedResponse,
            dependencies=[
                Depends(lambda: require_api_permission("sales.payments.read")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
            ])
async def list_customer_payments(
    limit: int = Query(100), 
    offset: int = Query(0), 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = CustomerPaymentService(db)
    payments, total = service.list_payments(skip=offset, limit=limit)
    return CustomerPaymentPaginatedResponse(items=[CustomerPaymentResponse.from_orm(p) for p in payments], total=total, limit=limit, offset=offset, has_more=(offset+len(payments))<total)

@router.get("/{payment_id}", 
            response_model=CustomerPaymentResponse,
            dependencies=[
                Depends(lambda: require_api_permission("sales.payments.read")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
            ])
async def get_customer_payment(
    payment_id: UUID, 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = CustomerPaymentService(db)
    payment = service.get_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return CustomerPaymentResponse.from_orm(payment)

@router.put("/{payment_id}", 
            response_model=CustomerPaymentResponse,
            dependencies=[
                Depends(lambda: require_api_permission("sales.payments.update")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
            ])
async def update_customer_payment(
    payment_id: UUID, 
    payment_data: CustomerPaymentUpdate, 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = CustomerPaymentService(db)
    payment = service.update_payment(payment_id, payment_data)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return CustomerPaymentResponse.from_orm(payment)

@router.delete("/{payment_id}",
               dependencies=[
                   Depends(lambda: require_api_permission("sales.payments.delete")),
                   Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
               ])
async def delete_customer_payment(
    payment_id: UUID, 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = CustomerPaymentService(db)
    success = service.delete_payment(payment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"success": True}
