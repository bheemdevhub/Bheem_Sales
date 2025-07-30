from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from bheem_core.core.database import get_db
from bheem_core.modules.auth.core.services.permissions_service import (
    require_roles, require_api_permission, get_current_user_id, get_current_company_id
)
from bheem_core.shared.models import UserRole
from bheem_core.modules.sales.core.services.bulk_operations_service import BulkOperationsService

router = APIRouter(prefix="/bulk-operations", tags=["Bulk Operations"])

@router.post("/import-sales-activities",
             dependencies=[
                 Depends(lambda: require_api_permission("sales.bulk.import")),
                 Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
             ])
async def import_sales_activities(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = BulkOperationsService(db)
    result = service.import_sales_activities(file)
    return result

@router.post("/export-sales-activities",
             dependencies=[
                 Depends(lambda: require_api_permission("sales.bulk.export")),
                 Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
             ])
async def export_sales_activities(
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = BulkOperationsService(db)
    result = service.export_sales_activities()
    return result

@router.post("/batch-update-payments",
             dependencies=[
                 Depends(lambda: require_api_permission("sales.bulk.update")),
                 Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
             ])
async def batch_update_payments(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = BulkOperationsService(db)
    result = service.batch_update_payments(file)
    return result

