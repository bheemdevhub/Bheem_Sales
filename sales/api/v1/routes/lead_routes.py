from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session
from uuid import UUID
from bheem_core.core.database import get_db
from bheem_core.modules.auth.core.services.permissions_service import (
    require_roles, require_api_permission, get_current_user_id, get_current_company_id
)
from bheem_core.shared.models import UserRole
from bheem_core.modules.sales.core.schemas.lead_schemas import LeadCreate, LeadUpdate, LeadResponse, LeadPaginatedResponse
from bheem_core.modules.sales.core.services.lead_service import LeadService

router = APIRouter(prefix="/leads", tags=["Leads"])

@router.post("/", response_model=LeadResponse,
          dependencies=[
              Depends(lambda: require_api_permission("lead.create")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
          ])
async def create_lead(
    lead_data: LeadCreate, 
    db: Session = Depends(get_db), 
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = LeadService(db)
    lead = service.create_lead(lead_data, current_user_id, company_id)
    return LeadResponse.from_orm(lead)

@router.get("/", response_model=LeadPaginatedResponse,
         dependencies=[
             Depends(lambda: require_api_permission("lead.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
         ])
async def list_leads(
    limit: int = Query(100), 
    offset: int = Query(0), 
    db: Session = Depends(get_db), 
    company_id: UUID = Depends(get_current_company_id)
):
    service = LeadService(db)
    leads, total = service.list_leads(company_id=company_id, skip=offset, limit=limit)
    return LeadPaginatedResponse(items=[LeadResponse.from_orm(l) for l in leads], total=total, limit=limit, offset=offset, has_more=(offset+len(leads))<total)

@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: str, db: Session = Depends(get_db), company_id: UUID = Query(...)):
    service = LeadService(db)
    lead = service.get_lead_by_id(lead_id, company_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadResponse.from_orm(lead)

@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(lead_id: str, lead_data: LeadUpdate, db: Session = Depends(get_db), company_id: UUID = Query(...), current_user_id: UUID = Depends(get_current_user_id)):
    service = LeadService(db)
    lead = service.update_lead(lead_id, company_id, lead_data, current_user_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadResponse.from_orm(lead)

@router.delete("/{lead_id}")
async def delete_lead(lead_id: str, db: Session = Depends(get_db), company_id: UUID = Query(...)):
    service = LeadService(db)
    lead = service.get_lead_by_id(lead_id, company_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    db.delete(lead)
    db.commit()
    return {"success": True}

