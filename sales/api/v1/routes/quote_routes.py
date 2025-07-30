from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session
from uuid import UUID

from bheem_core.core.database import get_db
from bheem_core.modules.auth.core.services.permissions_service import (
    require_roles, require_api_permission, get_current_user_id, get_current_company_id
)
from bheem_core.shared.models import UserRole
from bheem_core.modules.sales.core.schemas.quote_schemas import QuoteCreate, QuoteUpdate, QuoteResponse, QuotePaginatedResponse
from bheem_core.modules.sales.core.services.quote_service import QuoteService

router = APIRouter(prefix="/quotes", tags=["Quotes"])

@router.post("/", 
             response_model=QuoteResponse,
             dependencies=[
                 Depends(lambda: require_api_permission("sales.quotes.create")),
                 Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
             ])
async def create_quote(
    quote_data: QuoteCreate, 
    db: Session = Depends(get_db), 
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = QuoteService(db)
    quote = service.create_quote(quote_data, current_user_id)
    return QuoteResponse.from_orm(quote)

@router.get("/", 
            response_model=QuotePaginatedResponse,
            dependencies=[
                Depends(lambda: require_api_permission("sales.quotes.read")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
            ])
async def list_quotes(
    limit: int = Query(100), 
    offset: int = Query(0), 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = QuoteService(db)
    quotes, total = service.list_quotes(skip=offset, limit=limit)
    return QuotePaginatedResponse(items=[QuoteResponse.from_orm(q) for q in quotes], total=total, limit=limit, offset=offset, has_more=(offset+len(quotes))<total)

@router.get("/{quote_id}", 
            response_model=QuoteResponse,
            dependencies=[
                Depends(lambda: require_api_permission("sales.quotes.read")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
            ])
async def get_quote(
    quote_id: str, 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = QuoteService(db)
    quote = service.get_quote_by_id(quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    return QuoteResponse.from_orm(quote)

@router.put("/{quote_id}", 
            response_model=QuoteResponse,
            dependencies=[
                Depends(lambda: require_api_permission("sales.quotes.update")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
            ])
async def update_quote(
    quote_id: str, 
    quote_data: QuoteUpdate, 
    db: Session = Depends(get_db), 
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = QuoteService(db)
    quote = service.update_quote(quote_id, quote_data, current_user_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    return QuoteResponse.from_orm(quote)

@router.delete("/{quote_id}",
               dependencies=[
                   Depends(lambda: require_api_permission("sales.quotes.delete")),
                   Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
               ])
async def delete_quote(
    quote_id: str, 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    service = QuoteService(db)
    quote = service.get_quote_by_id(quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    db.delete(quote)
    db.commit()
    return {"success": True}

