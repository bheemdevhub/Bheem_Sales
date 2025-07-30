from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID

from bheem_core.core.database import get_db
from bheem_core.modules.auth.core.services.permissions_service import (
    require_roles, require_api_permission, get_current_user_id, get_current_company_id
)
from bheem_core.shared.models import UserRole
from bheem_core.modules.sales.core.schemas.sales_activity_schemas import (
    SalesActivityCreate, SalesActivityUpdate, SalesActivityResponse, SalesActivityPaginatedResponse
)
from bheem_core.modules.sales.core.services.sales_activity_service import SalesActivityService
from bheem_core.modules.sales.events.sales_activity_events import (
    SalesActivityCreatedEvent, SalesActivityUpdatedEvent, SalesActivityCompletedEvent, SalesActivityEventDispatcher
)

router = APIRouter(prefix="/sales-activities", tags=["Sales Activities"])
dispatcher = SalesActivityEventDispatcher()

@router.post("/", 
             response_model=SalesActivityResponse,
             dependencies=[
                 Depends(lambda: require_api_permission("sales.activities.create")),
                 Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
             ])
async def create_sales_activity(
    activity_data: SalesActivityCreate, 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = SalesActivityService(db)
    activity = service.create_activity(activity_data)
    dispatcher.dispatch(SalesActivityCreatedEvent(activity.id))
    return SalesActivityResponse.from_orm(activity)

@router.get("/", 
            response_model=SalesActivityPaginatedResponse,
            dependencies=[
                Depends(lambda: require_api_permission("sales.activities.read")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
            ])
async def list_sales_activities(
    limit: int = Query(100), 
    offset: int = Query(0), 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = SalesActivityService(db)
    activities, total = service.list_activities(skip=offset, limit=limit)
    return SalesActivityPaginatedResponse(
        items=[SalesActivityResponse.from_orm(a) for a in activities],
        total=total, limit=limit, offset=offset, has_more=(offset+len(activities))<total
    )

@router.get("/{activity_id}", 
            response_model=SalesActivityResponse,
            dependencies=[
                Depends(lambda: require_api_permission("sales.activities.read")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
            ])
async def get_sales_activity(
    activity_id: UUID, 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = SalesActivityService(db)
    activity = service.get_activity(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return SalesActivityResponse.from_orm(activity)

@router.put("/{activity_id}", 
            response_model=SalesActivityResponse,
            dependencies=[
                Depends(lambda: require_api_permission("sales.activities.update")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
            ])
async def update_sales_activity(
    activity_id: UUID, 
    activity_data: SalesActivityUpdate, 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = SalesActivityService(db)
    activity = service.update_activity(activity_id, activity_data)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    dispatcher.dispatch(SalesActivityUpdatedEvent(activity.id))
    return SalesActivityResponse.from_orm(activity)

@router.delete("/{activity_id}",
               dependencies=[
                   Depends(lambda: require_api_permission("sales.activities.delete")),
                   Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
               ])
async def delete_sales_activity(
    activity_id: UUID, 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = SalesActivityService(db)
    success = service.delete_activity(activity_id)
    if not success:
        raise HTTPException(status_code=404, detail="Activity not found")
    return {"success": True}

@router.post("/{activity_id}/complete", 
             response_model=SalesActivityResponse,
             dependencies=[
                 Depends(lambda: require_api_permission("sales.activities.complete")),
                 Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
             ])
async def complete_sales_activity(
    activity_id: UUID, 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = SalesActivityService(db)
    activity = service.complete_activity(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    dispatcher.dispatch(SalesActivityCompletedEvent(activity.id))
    return SalesActivityResponse.from_orm(activity)

