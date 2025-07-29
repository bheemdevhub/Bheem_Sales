from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from app.core.database import get_db
from app.modules.auth.core.services.permissions_service import (
    require_roles, require_api_permission, get_current_user_id, get_current_company_id
)
from app.shared.models import UserRole
from app.modules.sales.core.schemas.crm_schemas import (
    CRMAccountCreate, CRMAccountUpdate, CRMAccountResponse, CRMAccountPaginatedResponse,
    CRMContactCreate, CRMContactUpdate, CRMContactResponse, CRMContactPaginatedResponse,
    CRMInteractionCreate, CRMInteractionResponse, CRMPipelineResponse,
    CRMDashboardResponse, CRMLeadScoringResponse
)
from app.modules.sales.core.services.crm_service import CRMService

router = APIRouter(prefix="/crm", tags=["CRM Management"])

# ==================== CRM ACCOUNTS ====================

@router.post("/accounts", response_model=CRMAccountResponse, status_code=status.HTTP_201_CREATED,
          dependencies=[
              Depends(lambda: require_api_permission("crm.account.create")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
          ])
async def create_crm_account(
    account_data: CRMAccountCreate,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Create a new CRM account"""
    service = CRMService(db)
    return service.create_account(account_data, current_user_id, company_id)

@router.get("/accounts", response_model=CRMAccountPaginatedResponse,
         dependencies=[
             Depends(lambda: require_api_permission("crm.account.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
         ])
async def list_crm_accounts(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
    assigned_to: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """List CRM accounts with filtering and pagination"""
    service = CRMService(db)
    return service.list_accounts(limit, offset, company_id, search, assigned_to)

@router.get("/accounts/{account_id}", response_model=CRMAccountResponse,
         dependencies=[
             Depends(lambda: require_api_permission("crm.account.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
         ])
async def get_crm_account(
    account_id: str = Path(...),
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get CRM account by ID"""
    service = CRMService(db)
    return service.get_account(account_id, company_id)

@router.put("/accounts/{account_id}", response_model=CRMAccountResponse,
         dependencies=[
             Depends(lambda: require_api_permission("crm.account.update")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
         ])
async def update_crm_account(
    account_id: str = Path(...),
    account_data: CRMAccountUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Update CRM account"""
    service = CRMService(db)
    return service.update_account(account_id, account_data, current_user_id, company_id)

# ==================== CRM CONTACTS ====================

@router.post("/contacts", response_model=CRMContactResponse, status_code=status.HTTP_201_CREATED,
          dependencies=[
              Depends(lambda: require_api_permission("crm.contact.create")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
          ])
async def create_crm_contact(
    contact_data: CRMContactCreate,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Create a new CRM contact"""
    service = CRMService(db)
    return service.create_contact(contact_data, current_user_id, company_id)

@router.get("/contacts", response_model=CRMContactPaginatedResponse,
         dependencies=[
             Depends(lambda: require_api_permission("crm.contact.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
         ])
async def list_crm_contacts(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    lead_score: Optional[str] = Query(None),
    assigned_to: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """List CRM contacts with filtering and pagination"""
    service = CRMService(db)
    return service.list_contacts(limit, offset, company_id, search, status, lead_score, assigned_to)

@router.get("/contacts/{contact_id}", response_model=CRMContactResponse,
         dependencies=[
             Depends(lambda: require_api_permission("crm.contact.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
         ])
async def get_crm_contact(
    contact_id: str = Path(...),
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get CRM contact by ID"""
    service = CRMService(db)
    return service.get_contact(contact_id, company_id)

@router.put("/contacts/{contact_id}", response_model=CRMContactResponse,
         dependencies=[
             Depends(lambda: require_api_permission("crm.contact.update")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
         ])
async def update_crm_contact(
    contact_id: str = Path(...),
    contact_data: CRMContactUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Update CRM contact"""
    service = CRMService(db)
    return service.update_contact(contact_id, contact_data, current_user_id, company_id)

# ==================== CRM INTERACTIONS ====================

@router.post("/contacts/{contact_id}/interactions", response_model=CRMInteractionResponse,
          dependencies=[
              Depends(lambda: require_api_permission("crm.interaction.create")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
          ])
async def create_crm_interaction(
    contact_id: str = Path(...),
    interaction_data: CRMInteractionCreate = Body(...),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Create a new CRM interaction"""
    service = CRMService(db)
    return service.create_interaction(contact_id, interaction_data, current_user_id, company_id)

@router.get("/contacts/{contact_id}/interactions", response_model=List[CRMInteractionResponse],
         dependencies=[
             Depends(lambda: require_api_permission("crm.interaction.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
         ])
async def list_crm_interactions(
    contact_id: str = Path(...),
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """List interactions for a contact"""
    service = CRMService(db)
    return service.list_interactions(contact_id, company_id)

# ==================== CRM PIPELINE & ANALYTICS ====================

@router.get("/pipeline", response_model=CRMPipelineResponse,
         dependencies=[
             Depends(lambda: require_api_permission("crm.pipeline.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
         ])
async def get_crm_pipeline(
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get CRM pipeline overview"""
    service = CRMService(db)
    return service.get_pipeline(company_id)

@router.get("/dashboard", response_model=CRMDashboardResponse,
         dependencies=[
             Depends(lambda: require_api_permission("crm.dashboard.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
         ])
async def get_crm_dashboard(
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get CRM dashboard data"""
    service = CRMService(db)
    return service.get_dashboard(company_id)

@router.post("/contacts/{contact_id}/score", response_model=CRMLeadScoringResponse,
          dependencies=[
              Depends(lambda: require_api_permission("crm.lead.score")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
          ])
async def score_lead(
    contact_id: str = Path(...),
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """Calculate lead score for a contact"""
    service = CRMService(db)
    return service.calculate_lead_score(contact_id, company_id)

# ==================== CRM BULK OPERATIONS ====================

@router.post("/contacts/bulk-update", response_model=dict,
          dependencies=[
              Depends(lambda: require_api_permission("crm.contact.bulk_update")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
          ])
async def bulk_update_contacts(
    updates: List[dict] = Body(...),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Bulk update contacts"""
    service = CRMService(db)
    return service.bulk_update_contacts(updates, current_user_id, company_id)

@router.post("/contacts/bulk-assign", response_model=dict,
          dependencies=[
              Depends(lambda: require_api_permission("crm.contact.bulk_assign")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
          ])
async def bulk_assign_contacts(
    contact_ids: List[str] = Body(...),
    assigned_to: UUID = Body(...),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Bulk assign contacts to a user"""
    service = CRMService(db)
    return service.bulk_assign_contacts(contact_ids, assigned_to, current_user_id, company_id)
