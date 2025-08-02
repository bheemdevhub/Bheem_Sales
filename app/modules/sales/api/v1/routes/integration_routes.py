from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional, Dict, Any
from app.core.database import get_db
from app.modules.auth.core.services.permissions_service import (
    require_roles, require_api_permission, get_current_user_id, get_current_company_id
)
from app.shared.models import UserRole
from app.modules.sales.core.schemas.integration_schemas import (
    IntegrationConfigCreate, IntegrationConfigUpdate, IntegrationConfigResponse,
    WebhookConfigCreate, WebhookConfigResponse, WebhookEventResponse,
    ExternalSyncRequest, ExternalSyncResponse, IntegrationHealthResponse
)
from app.modules.sales.core.services.integration_service import IntegrationService

router = APIRouter(prefix="/integrations", tags=["External Integrations"])

# ==================== INTEGRATION CONFIGURATION ====================

@router.post("/config", response_model=IntegrationConfigResponse, status_code=status.HTTP_201_CREATED,
          dependencies=[
              Depends(lambda: require_api_permission("integration.config.create")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
          ])
async def create_integration_config(
    config_data: IntegrationConfigCreate,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Create integration configuration"""
    service = IntegrationService(db)
    return service.create_config(config_data, current_user_id, company_id)

@router.get("/config", response_model=List[IntegrationConfigResponse],
         dependencies=[
             Depends(lambda: require_api_permission("integration.config.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.VIEWER]))
         ])
async def list_integration_configs(
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """List integration configurations"""
    service = IntegrationService(db)
    return service.list_configs(company_id)

@router.get("/config/{config_id}", response_model=IntegrationConfigResponse,
         dependencies=[
             Depends(lambda: require_api_permission("integration.config.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.VIEWER]))
         ])
async def get_integration_config(
    config_id: UUID = Path(...),
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get integration configuration"""
    service = IntegrationService(db)
    return service.get_config(config_id, company_id)

@router.put("/config/{config_id}", response_model=IntegrationConfigResponse,
         dependencies=[
             Depends(lambda: require_api_permission("integration.config.update")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
         ])
async def update_integration_config(
    config_id: UUID = Path(...),
    config_data: IntegrationConfigUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Update integration configuration"""
    service = IntegrationService(db)
    return service.update_config(config_id, config_data, current_user_id, company_id)

@router.delete("/config/{config_id}", response_model=dict,
            dependencies=[
                Depends(lambda: require_api_permission("integration.config.delete")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
            ])
async def delete_integration_config(
    config_id: UUID = Path(...),
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """Delete integration configuration"""
    service = IntegrationService(db)
    return {"success": service.delete_config(config_id, company_id)}

# ==================== WEBHOOK MANAGEMENT ====================

@router.post("/webhooks", response_model=WebhookConfigResponse, status_code=status.HTTP_201_CREATED,
          dependencies=[
              Depends(lambda: require_api_permission("integration.webhook.create")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
          ])
async def create_webhook(
    webhook_data: WebhookConfigCreate,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Create webhook configuration"""
    service = IntegrationService(db)
    return service.create_webhook(webhook_data, current_user_id, company_id)

@router.get("/webhooks", response_model=List[WebhookConfigResponse],
         dependencies=[
             Depends(lambda: require_api_permission("integration.webhook.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.VIEWER]))
         ])
async def list_webhooks(
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """List webhook configurations"""
    service = IntegrationService(db)
    return service.list_webhooks(company_id)

@router.post("/webhooks/{webhook_id}/test", response_model=dict,
          dependencies=[
              Depends(lambda: require_api_permission("integration.webhook.test")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
          ])
async def test_webhook(
    webhook_id: UUID = Path(...),
    test_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """Test webhook configuration"""
    service = IntegrationService(db)
    return service.test_webhook(webhook_id, test_data, company_id)

@router.get("/webhooks/{webhook_id}/events", response_model=List[WebhookEventResponse],
         dependencies=[
             Depends(lambda: require_api_permission("integration.webhook.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.VIEWER]))
         ])
async def list_webhook_events(
    webhook_id: UUID = Path(...),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """List webhook events"""
    service = IntegrationService(db)
    return service.list_webhook_events(webhook_id, limit, offset, company_id)

# ==================== EXTERNAL SYSTEM SYNC ====================

@router.post("/sync/salesforce", response_model=ExternalSyncResponse,
          dependencies=[
              Depends(lambda: require_api_permission("integration.sync.salesforce")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
          ])
async def sync_salesforce(
    sync_request: ExternalSyncRequest,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Sync data with Salesforce"""
    service = IntegrationService(db)
    return service.sync_salesforce(sync_request, current_user_id, company_id)

@router.post("/sync/hubspot", response_model=ExternalSyncResponse,
          dependencies=[
              Depends(lambda: require_api_permission("integration.sync.hubspot")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
          ])
async def sync_hubspot(
    sync_request: ExternalSyncRequest,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Sync data with HubSpot"""
    service = IntegrationService(db)
    return service.sync_hubspot(sync_request, current_user_id, company_id)

@router.post("/sync/pipedrive", response_model=ExternalSyncResponse,
          dependencies=[
              Depends(lambda: require_api_permission("integration.sync.pipedrive")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
          ])
async def sync_pipedrive(
    sync_request: ExternalSyncRequest,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Sync data with Pipedrive"""
    service = IntegrationService(db)
    return service.sync_pipedrive(sync_request, current_user_id, company_id)

@router.post("/sync/custom", response_model=ExternalSyncResponse,
          dependencies=[
              Depends(lambda: require_api_permission("integration.sync.custom")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
          ])
async def sync_custom_system(
    system_name: str = Body(...),
    sync_request: ExternalSyncRequest = Body(...),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Sync data with custom external system"""
    service = IntegrationService(db)
    return service.sync_custom_system(system_name, sync_request, current_user_id, company_id)

# ==================== INTEGRATION HEALTH & MONITORING ====================

@router.get("/health", response_model=List[IntegrationHealthResponse],
         dependencies=[
             Depends(lambda: require_api_permission("integration.health.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.VIEWER]))
         ])
async def get_integration_health(
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get health status of all integrations"""
    service = IntegrationService(db)
    return service.get_health_status(company_id)

@router.get("/health/{integration_name}", response_model=IntegrationHealthResponse,
         dependencies=[
             Depends(lambda: require_api_permission("integration.health.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.VIEWER]))
         ])
async def get_specific_integration_health(
    integration_name: str = Path(...),
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get health status of specific integration"""
    service = IntegrationService(db)
    return service.get_specific_health(integration_name, company_id)

@router.post("/health/{integration_name}/test", response_model=dict,
          dependencies=[
              Depends(lambda: require_api_permission("integration.health.test")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
          ])
async def test_integration_connection(
    integration_name: str = Path(...),
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """Test connection to specific integration"""
    service = IntegrationService(db)
    return service.test_connection(integration_name, company_id)

# ==================== DATA MAPPING & TRANSFORMATION ====================

@router.post("/mapping/{integration_name}", response_model=dict,
          dependencies=[
              Depends(lambda: require_api_permission("integration.mapping.create")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
          ])
async def create_data_mapping(
    integration_name: str = Path(...),
    mapping_config: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Create data mapping for integration"""
    service = IntegrationService(db)
    return service.create_data_mapping(integration_name, mapping_config, current_user_id, company_id)

@router.get("/mapping/{integration_name}", response_model=dict,
         dependencies=[
             Depends(lambda: require_api_permission("integration.mapping.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.VIEWER]))
         ])
async def get_data_mapping(
    integration_name: str = Path(...),
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get data mapping for integration"""
    service = IntegrationService(db)
    return service.get_data_mapping(integration_name, company_id)

@router.put("/mapping/{integration_name}", response_model=dict,
         dependencies=[
             Depends(lambda: require_api_permission("integration.mapping.update")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
         ])
async def update_data_mapping(
    integration_name: str = Path(...),
    mapping_config: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Update data mapping for integration"""
    service = IntegrationService(db)
    return service.update_data_mapping(integration_name, mapping_config, current_user_id, company_id)
