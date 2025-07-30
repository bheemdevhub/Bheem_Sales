from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from bheem_core.core.database import get_db
from bheem_core.modules.auth.core.services.permissions_service import (
    require_roles, require_api_permission, get_current_user_id, get_current_company_id
)
from bheem_core.shared.models import UserRole
from bheem_core.modules.sales.core.schemas.automation_schemas import (
    SalesWorkflowCreate, SalesWorkflowUpdate, SalesWorkflowResponse,
    SalesRuleCreate, SalesRuleUpdate, SalesRuleResponse,
    SalesAutomationTrigger, SalesAutomationAction, SalesAutomationExecutionResponse,
    SalesSequenceCreate, SalesSequenceUpdate, SalesSequenceResponse,
    SalesTaskCreate, SalesTaskUpdate, SalesTaskResponse,
    SalesReminderCreate, SalesReminderResponse, SalesNotificationResponse
)
from bheem_core.modules.sales.core.services.automation_service import SalesAutomationService

router = APIRouter(prefix="/automation", tags=["Sales Automation"])

# ==================== SALES WORKFLOWS ====================

@router.post("/workflows", response_model=SalesWorkflowResponse, status_code=status.HTTP_201_CREATED,
          dependencies=[
              Depends(lambda: require_api_permission("sales.workflow.create")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
          ])
async def create_sales_workflow(
    workflow_data: SalesWorkflowCreate,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Create sales workflow"""
    service = SalesAutomationService(db)
    return service.create_workflow(workflow_data, current_user_id, company_id)

@router.get("/workflows", response_model=List[SalesWorkflowResponse],
         dependencies=[
             Depends(lambda: require_api_permission("sales.workflow.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
         ])
async def list_sales_workflows(
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """List sales workflows"""
    service = SalesAutomationService(db)
    return service.list_workflows(company_id, active_only)

@router.get("/workflows/{workflow_id}", response_model=SalesWorkflowResponse,
         dependencies=[
             Depends(lambda: require_api_permission("sales.workflow.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
         ])
async def get_sales_workflow(
    workflow_id: UUID = Path(...),
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get sales workflow"""
    service = SalesAutomationService(db)
    return service.get_workflow(workflow_id, company_id)

@router.put("/workflows/{workflow_id}", response_model=SalesWorkflowResponse,
         dependencies=[
             Depends(lambda: require_api_permission("sales.workflow.update")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
         ])
async def update_sales_workflow(
    workflow_id: UUID = Path(...),
    workflow_data: SalesWorkflowUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Update sales workflow"""
    service = SalesAutomationService(db)
    return service.update_workflow(workflow_id, workflow_data, current_user_id, company_id)

@router.post("/workflows/{workflow_id}/activate", response_model=SalesWorkflowResponse,
          dependencies=[
              Depends(lambda: require_api_permission("sales.workflow.activate")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
          ])
async def activate_sales_workflow(
    workflow_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Activate sales workflow"""
    service = SalesAutomationService(db)
    return service.activate_workflow(workflow_id, current_user_id, company_id)

@router.post("/workflows/{workflow_id}/deactivate", response_model=SalesWorkflowResponse,
          dependencies=[
              Depends(lambda: require_api_permission("sales.workflow.deactivate")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
          ])
async def deactivate_sales_workflow(
    workflow_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Deactivate sales workflow"""
    service = SalesAutomationService(db)
    return service.deactivate_workflow(workflow_id, current_user_id, company_id)

# ==================== SALES RULES ====================

@router.post("/rules", response_model=SalesRuleResponse, status_code=status.HTTP_201_CREATED,
          dependencies=[
              Depends(lambda: require_api_permission("sales.rule.create")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
          ])
async def create_sales_rule(
    rule_data: SalesRuleCreate,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Create sales rule"""
    service = SalesAutomationService(db)
    return service.create_rule(rule_data, current_user_id, company_id)

@router.get("/rules", response_model=List[SalesRuleResponse],
         dependencies=[
             Depends(lambda: require_api_permission("sales.rule.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
         ])
async def list_sales_rules(
    rule_type: Optional[str] = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """List sales rules"""
    service = SalesAutomationService(db)
    return service.list_rules(company_id, rule_type, active_only)

@router.post("/rules/{rule_id}/execute", response_model=SalesAutomationExecutionResponse,
          dependencies=[
              Depends(lambda: require_api_permission("sales.rule.execute")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
          ])
async def execute_sales_rule(
    rule_id: UUID = Path(...),
    execution_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Execute sales rule"""
    service = SalesAutomationService(db)
    return service.execute_rule(rule_id, execution_data, current_user_id, company_id)

# ==================== SALES SEQUENCES ====================

@router.post("/sequences", response_model=SalesSequenceResponse, status_code=status.HTTP_201_CREATED,
          dependencies=[
              Depends(lambda: require_api_permission("sales.sequence.create")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
          ])
async def create_sales_sequence(
    sequence_data: SalesSequenceCreate,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Create sales sequence"""
    service = SalesAutomationService(db)
    return service.create_sequence(sequence_data, current_user_id, company_id)

@router.get("/sequences", response_model=List[SalesSequenceResponse],
         dependencies=[
             Depends(lambda: require_api_permission("sales.sequence.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
         ])
async def list_sales_sequences(
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """List sales sequences"""
    service = SalesAutomationService(db)
    return service.list_sequences(company_id, active_only)

@router.post("/sequences/{sequence_id}/enroll", response_model=dict,
          dependencies=[
              Depends(lambda: require_api_permission("sales.sequence.enroll")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
          ])
async def enroll_in_sequence(
    sequence_id: UUID = Path(...),
    contact_ids: List[str] = Body(...),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Enroll contacts in sales sequence"""
    service = SalesAutomationService(db)
    return service.enroll_in_sequence(sequence_id, contact_ids, current_user_id, company_id)

@router.post("/sequences/{sequence_id}/unenroll", response_model=dict,
          dependencies=[
              Depends(lambda: require_api_permission("sales.sequence.unenroll")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
          ])
async def unenroll_from_sequence(
    sequence_id: UUID = Path(...),
    contact_ids: List[str] = Body(...),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Unenroll contacts from sales sequence"""
    service = SalesAutomationService(db)
    return service.unenroll_from_sequence(sequence_id, contact_ids, current_user_id, company_id)

# ==================== SALES TASKS ====================

@router.post("/tasks", response_model=SalesTaskResponse, status_code=status.HTTP_201_CREATED,
          dependencies=[
              Depends(lambda: require_api_permission("sales.task.create")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
          ])
async def create_sales_task(
    task_data: SalesTaskCreate,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Create sales task"""
    service = SalesAutomationService(db)
    return service.create_task(task_data, current_user_id, company_id)

@router.get("/tasks", response_model=List[SalesTaskResponse],
         dependencies=[
             Depends(lambda: require_api_permission("sales.task.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
         ])
async def list_sales_tasks(
    assigned_to: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    due_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """List sales tasks"""
    service = SalesAutomationService(db)
    return service.list_tasks(company_id, assigned_to, status, due_date)

@router.put("/tasks/{task_id}", response_model=SalesTaskResponse,
         dependencies=[
             Depends(lambda: require_api_permission("sales.task.update")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
         ])
async def update_sales_task(
    task_id: UUID = Path(...),
    task_data: SalesTaskUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Update sales task"""
    service = SalesAutomationService(db)
    return service.update_task(task_id, task_data, current_user_id, company_id)

@router.post("/tasks/{task_id}/complete", response_model=SalesTaskResponse,
          dependencies=[
              Depends(lambda: require_api_permission("sales.task.complete")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
          ])
async def complete_sales_task(
    task_id: UUID = Path(...),
    completion_notes: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Complete sales task"""
    service = SalesAutomationService(db)
    return service.complete_task(task_id, completion_notes, current_user_id, company_id)

# ==================== SALES REMINDERS ====================

@router.post("/reminders", response_model=SalesReminderResponse, status_code=status.HTTP_201_CREATED,
          dependencies=[
              Depends(lambda: require_api_permission("sales.reminder.create")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
          ])
async def create_sales_reminder(
    reminder_data: SalesReminderCreate,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Create sales reminder"""
    service = SalesAutomationService(db)
    return service.create_reminder(reminder_data, current_user_id, company_id)

@router.get("/reminders", response_model=List[SalesReminderResponse],
         dependencies=[
             Depends(lambda: require_api_permission("sales.reminder.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
         ])
async def list_sales_reminders(
    user_id: Optional[UUID] = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """List sales reminders"""
    service = SalesAutomationService(db)
    target_user = user_id if user_id else current_user_id
    return service.list_reminders(target_user, company_id, active_only)

@router.post("/reminders/{reminder_id}/snooze", response_model=SalesReminderResponse,
          dependencies=[
              Depends(lambda: require_api_permission("sales.reminder.snooze")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
          ])
async def snooze_sales_reminder(
    reminder_id: UUID = Path(...),
    snooze_until: datetime = Body(...),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Snooze sales reminder"""
    service = SalesAutomationService(db)
    return service.snooze_reminder(reminder_id, snooze_until, current_user_id, company_id)

# ==================== SALES NOTIFICATIONS ====================

@router.get("/notifications", response_model=List[SalesNotificationResponse],
         dependencies=[
             Depends(lambda: require_api_permission("sales.notification.read")),
             Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP, UserRole.VIEWER]))
         ])
async def list_sales_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """List sales notifications"""
    service = SalesAutomationService(db)
    return service.list_notifications(current_user_id, company_id, unread_only, limit)

@router.post("/notifications/{notification_id}/read", response_model=dict,
          dependencies=[
              Depends(lambda: require_api_permission("sales.notification.read")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
          ])
async def mark_notification_read(
    notification_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Mark notification as read"""
    service = SalesAutomationService(db)
    return service.mark_notification_read(notification_id, current_user_id, company_id)

@router.post("/notifications/read-all", response_model=dict,
          dependencies=[
              Depends(lambda: require_api_permission("sales.notification.read")),
              Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
          ])
async def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Mark all notifications as read"""
    service = SalesAutomationService(db)
    return service.mark_all_notifications_read(current_user_id, company_id)

