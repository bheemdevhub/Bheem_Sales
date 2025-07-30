from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session
from uuid import UUID

from bheem_core.core.database import get_db
from bheem_core.modules.auth.core.services.permissions_service import (
    require_roles, require_api_permission, get_current_user_id, get_current_company_id
)
from bheem_core.shared.models import UserRole
from bheem_core.modules.sales.core.schemas.vendor_schemas import VendorCreate, VendorUpdate, VendorResponse, VendorPaginatedResponse
from bheem_core.modules.sales.core.services.vendor_service import VendorService

router = APIRouter(prefix="/vendors", tags=["Vendors"])

@router.post("/", 
             response_model=VendorResponse,
             dependencies=[
                 Depends(lambda: require_api_permission("sales.vendors.create")),
                 Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
             ])
async def create_vendor(
    vendor_data: VendorCreate, 
    db: Session = Depends(get_db), 
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = VendorService(db)
    vendor = service.create_vendor(vendor_data, current_user_id)
    return VendorResponse.from_orm(vendor)

@router.get("/", 
            response_model=VendorPaginatedResponse,
            dependencies=[
                Depends(lambda: require_api_permission("sales.vendors.read")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
            ])
async def list_vendors(
    limit: int = Query(100), 
    offset: int = Query(0), 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = VendorService(db)
    vendors, total = service.list_vendors(skip=offset, limit=limit)
    return VendorPaginatedResponse(items=[VendorResponse.from_orm(v) for v in vendors], total=total, limit=limit, offset=offset, has_more=(offset+len(vendors))<total)

@router.get("/{vendor_id}", 
            response_model=VendorResponse,
            dependencies=[
                Depends(lambda: require_api_permission("sales.vendors.read")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
            ])
async def get_vendor(
    vendor_id: str, 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = VendorService(db)
    vendor = service.get_vendor_by_id(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return VendorResponse.from_orm(vendor)

@router.put("/{vendor_id}", 
            response_model=VendorResponse,
            dependencies=[
                Depends(lambda: require_api_permission("sales.vendors.update")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
            ])
async def update_vendor(
    vendor_id: str, 
    vendor_data: VendorUpdate, 
    db: Session = Depends(get_db), 
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = VendorService(db)
    vendor = service.update_vendor(vendor_id, vendor_data, current_user_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return VendorResponse.from_orm(vendor)

@router.delete("/{vendor_id}",
               dependencies=[
                   Depends(lambda: require_api_permission("sales.vendors.delete")),
                   Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
               ])
async def delete_vendor(
    vendor_id: str, 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = VendorService(db)
    vendor = service.get_vendor_by_id(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    db.delete(vendor)
    db.commit()
    return {"success": True}

