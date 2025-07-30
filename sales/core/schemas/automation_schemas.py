from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel, Field


# Sales Workflow Schemas
class SalesWorkflowCreate(BaseModel):
    workflow_name: str
    description: Optional[str] = None
    trigger_type: str
    trigger_conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    company_id: UUID

class SalesWorkflowUpdate(BaseModel):
    workflow_name: Optional[str] = None
    description: Optional[str] = None
    trigger_conditions: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None

class SalesWorkflowResponse(BaseModel):
    id: UUID
    workflow_name: str
    description: Optional[str] = None
    trigger_type: str
    trigger_conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    is_active: bool
    company_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# Sales Rule Schemas
class SalesRuleCreate(BaseModel):
    rule_name: str
    description: Optional[str] = None
    conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    priority: int = 1
    company_id: UUID

class SalesRuleUpdate(BaseModel):
    rule_name: Optional[str] = None
    description: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, Any]]] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None

class SalesRuleResponse(BaseModel):
    id: UUID
    rule_name: str
    description: Optional[str] = None
    conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    priority: int
    is_active: bool
    company_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# Automation Trigger/Action Schemas
class SalesAutomationTrigger(BaseModel):
    trigger_type: str
    trigger_event: str
    conditions: Dict[str, Any]

class SalesAutomationAction(BaseModel):
    action_type: str
    action_data: Dict[str, Any]
    delay_minutes: Optional[int] = 0

class SalesAutomationExecutionResponse(BaseModel):
    execution_id: UUID
    workflow_id: UUID
    trigger_data: Dict[str, Any]
    status: str
    executed_at: datetime
    results: List[Dict[str, Any]] = []


# Sales Sequence Schemas
class SalesSequenceCreate(BaseModel):
    sequence_name: str
    description: Optional[str] = None
    steps: List[Dict[str, Any]]
    company_id: UUID

class SalesSequenceUpdate(BaseModel):
    sequence_name: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None

class SalesSequenceResponse(BaseModel):
    id: UUID
    sequence_name: str
    description: Optional[str] = None
    steps: List[Dict[str, Any]]
    is_active: bool
    company_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# Sales Task Schemas
class SalesTaskCreate(BaseModel):
    task_title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    assigned_to: Optional[UUID] = None
    priority: str = "MEDIUM"
    company_id: UUID

class SalesTaskUpdate(BaseModel):
    task_title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    assigned_to: Optional[UUID] = None
    priority: Optional[str] = None
    status: Optional[str] = None

class SalesTaskResponse(BaseModel):
    id: UUID
    task_title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    assigned_to: Optional[UUID] = None
    priority: str
    status: str
    company_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# Sales Reminder Schemas
class SalesReminderCreate(BaseModel):
    reminder_type: str
    reminder_message: str
    remind_at: datetime
    entity_type: str
    entity_id: UUID
    company_id: UUID

class SalesReminderResponse(BaseModel):
    id: UUID
    reminder_type: str
    reminder_message: str
    remind_at: datetime
    entity_type: str
    entity_id: UUID
    is_sent: bool
    company_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# Sales Notification Schemas
class SalesNotificationResponse(BaseModel):
    id: UUID
    notification_type: str
    title: str
    message: str
    recipient_id: UUID
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

