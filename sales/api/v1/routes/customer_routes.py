from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.database import get_db
from app.modules.auth.core.services.permissions_service import (
    require_roles, require_api_permission, get_current_user_id, get_current_company_id
)
from app.shared.models import UserRole
from app.modules.sales.core.services.customer_service import CustomerService
from app.modules.sales.core.schemas.customer_schemas import CustomerCreate, CustomerUpdate, CustomerResponse, CustomerPaginatedResponse

router = APIRouter(prefix="/customers", tags=["Customer Management"], responses={404: {"description": "Not found"}})

@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED,
          dependencies=[
              Depends(lambda: require_api_permission("customer.create")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
          ])
async def create_customer(
    customer_data: CustomerCreate, 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = CustomerService(db)
    return service.create_customer(customer_data, current_user_id, company_id)

@router.get("/", response_model=CustomerPaginatedResponse,
         dependencies=[
             Depends(lambda: require_api_permission("customer.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
         ])
async def list_customers(
    limit: int = Query(100), 
    offset: int = Query(0), 
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    service = CustomerService(db)
    return service.list_customers(limit, offset, company_id)

@router.get("/{customer_id}", response_model=CustomerResponse,
         dependencies=[
             Depends(lambda: require_api_permission("customer.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
         ])
async def get_customer_by_id(
    customer_id: UUID = Path(...), 
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    service = CustomerService(db)
    return service.get_customer_by_id(customer_id, company_id)

@router.put("/{customer_id}", response_model=CustomerResponse,
         dependencies=[
             Depends(lambda: require_api_permission("customer.update")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
         ])
async def update_customer(
    customer_id: UUID = Path(...), 
    customer_data: CustomerUpdate = Body(...), 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = CustomerService(db)
    return service.update_customer(customer_id, customer_data, current_user_id, company_id)

@router.delete("/{customer_id}", response_model=dict,
            dependencies=[
                Depends(lambda: require_api_permission("customer.delete")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
            ])
async def delete_customer(
    customer_id: UUID = Path(...), 
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    service = CustomerService(db)
    return {"success": service.delete_customer(customer_id, company_id)}
