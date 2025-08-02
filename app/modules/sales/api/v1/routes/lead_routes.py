from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.database import get_db
from app.modules.auth.core.services.permissions_service import (
    require_roles, require_api_permission, get_current_user_id, get_current_company_id
)
from app.shared.models import UserRole
from app.modules.sales.core.schemas.lead_schemas import LeadCreate, LeadUpdate, LeadResponse, LeadPaginatedResponse
from app.modules.sales.core.services.lead_service import LeadService

router = APIRouter(prefix="/leads", tags=["Leads"])

@router.post("/", response_model=LeadResponse,
          dependencies=[
              Depends(lambda: require_api_permission("lead.create")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
          ])
async def create_lead(
    lead_data: LeadCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = LeadService(db)
    lead = await service.create_lead(lead_data, current_user_id, company_id)
    return LeadResponse.from_orm(lead)

@router.get("/", response_model=LeadPaginatedResponse,
         dependencies=[
             Depends(lambda: require_api_permission("lead.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
         ])
async def list_leads(
    limit: int = Query(100), 
    offset: int = Query(0), 
    db: AsyncSession = Depends(get_db), 
    company_id: UUID = Depends(get_current_company_id)
):
    service = LeadService(db)
    leads, total = await service.list_leads(company_id=company_id, skip=offset, limit=limit)
    return LeadPaginatedResponse(items=[LeadResponse.from_orm(l) for l in leads], total=total, limit=limit, offset=offset, has_more=(offset+len(leads))<total)

@router.get("/{lead_id}", response_model=LeadResponse,
         dependencies=[
             Depends(lambda: require_api_permission("lead.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
         ])
async def get_lead(
    lead_id: str = Path(...), 
    db: AsyncSession = Depends(get_db), 
    company_id: UUID = Depends(get_current_company_id)
):
    service = LeadService(db)
    lead = await service.get_lead_by_id(lead_id, company_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadResponse.from_orm(lead)

@router.put("/{lead_id}", response_model=LeadResponse,
         dependencies=[
             Depends(lambda: require_api_permission("lead.update")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
         ])
async def update_lead(
    lead_id: str = Path(...), 
    lead_data: LeadUpdate = Body(...), 
    db: AsyncSession = Depends(get_db), 
    company_id: UUID = Depends(get_current_company_id), 
    current_user_id: UUID = Depends(get_current_user_id)
):
    service = LeadService(db)
    lead = await service.update_lead(lead_id, company_id, lead_data, current_user_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadResponse.from_orm(lead)

@router.delete("/{lead_id}",
            dependencies=[
                Depends(lambda: require_api_permission("lead.delete")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
            ])
async def delete_lead(
    lead_id: str = Path(...), 
    db: AsyncSession = Depends(get_db), 
    company_id: UUID = Depends(get_current_company_id)
):
    service = LeadService(db)
    lead = await service.get_lead_by_id(lead_id, company_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    await db.delete(lead)
    await db.commit()
    return {"success": True}

@router.post("/{lead_id}/convert", 
           dependencies=[
               Depends(lambda: require_api_permission("lead.convert")),
               Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
           ])
async def convert_lead(
    lead_id: str = Path(...),
    db: AsyncSession = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id),
    current_user_id: UUID = Depends(get_current_user_id)
):
    service = LeadService(db)
    result = await service.convert_lead_to_customer(lead_id, company_id, current_user_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return result

@router.put("/{lead_id}/status",
          dependencies=[
              Depends(lambda: require_api_permission("lead.update")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
          ])
async def change_lead_status(
    lead_id: str = Path(...),
    new_status: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id),
    current_user_id: UUID = Depends(get_current_user_id)
):
    from app.modules.sales.core.models.sales_models import LeadStatus
    try:
        status_enum = LeadStatus(new_status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid lead status")
    
    service = LeadService(db)
    lead = await service.change_lead_status(lead_id, company_id, status_enum, current_user_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadResponse.from_orm(lead)

@router.post("/{lead_id}/activities",
           dependencies=[
               Depends(lambda: require_api_permission("lead.activity.create")),
               Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
           ])
async def add_lead_activity(
    lead_id: str = Path(...),
    activity_data: dict = Body(...),  # LeadActivity schema would be needed
    db: AsyncSession = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id),
    current_user_id: UUID = Depends(get_current_user_id)
):
    service = LeadService(db)
    # This would need proper LeadActivity schema implementation
    # For now, returning a placeholder
    return {"message": "Activity endpoint needs LeadActivity schema implementation"}

@router.get("/{lead_id}/activities",
          dependencies=[
              Depends(lambda: require_api_permission("lead.activity.read")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
          ])
async def get_lead_activities(
    lead_id: str = Path(...),
    skip: int = Query(0),
    limit: int = Query(100),
    db: AsyncSession = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    service = LeadService(db)
    activities, total = await service.get_lead_activities(lead_id, company_id, skip, limit)
    return {
        "items": [{"id": str(activity.id), "type": activity.activity_type, "subject": activity.subject} for activity in activities],
        "total": total,
        "limit": limit,
        "offset": skip
    }

@router.get("/analytics",
          dependencies=[
              Depends(lambda: require_api_permission("lead.analytics.read")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
          ])
async def get_lead_analytics(
    db: AsyncSession = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    service = LeadService(db)
    analytics = await service.get_lead_analytics(company_id)
    return analytics
