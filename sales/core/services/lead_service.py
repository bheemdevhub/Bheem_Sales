from typing import List, Optional, Dict, Any, Union, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, desc, asc
import logging
from datetime import datetime, date
from uuid import UUID
import uuid

from bheem_core.modules.sales.core.models.sales_models import Lead, LeadStatus, LeadSource
from bheem_core.modules.sales.core.schemas.lead_schemas import (
    LeadCreate, LeadUpdate, LeadSearchParams, LeadActivity
)
from bheem_core.modules.sales.events.lead_events import (
    LeadEventDispatcher, LeadCreatedEvent, LeadUpdatedEvent, 
    LeadStatusChangedEvent, LeadConvertedEvent, LeadActivityAddedEvent
)
from bheem_core.shared.models import Activity, ActivityType, ActivityStatus

logger = logging.getLogger(__name__)


class LeadService:
    """
    Service for managing lead-related operations
    Handles CRUD operations, search, conversion, and business logic for leads
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.event_dispatcher = LeadEventDispatcher()
    
    # Create operations
    
    def create_lead(self, lead_data: LeadCreate, current_user_id: UUID) -> Lead:
        """Create a new lead with basic information"""
        # Create a new lead ID (UUID)
        lead_id = str(uuid.uuid4())
        
        # Create the new Lead object
        new_lead = Lead(
            id=lead_id,
            first_name=lead_data.first_name,
            last_name=lead_data.last_name,
            email=lead_data.email,
            phone=lead_data.phone,
            mobile=lead_data.mobile,
            business_name=lead_data.business_name,
            industry=lead_data.industry,
            source=lead_data.source,
            status=lead_data.status,
            lead_score=lead_data.lead_score,
            sales_rep_id=lead_data.sales_rep_id,
            notes=lead_data.notes,
            custom_fields=lead_data.custom_fields or {},
            address_line1=lead_data.address_line1,
            address_line2=lead_data.address_line2,
            city=lead_data.city,
            state=lead_data.state,
            postal_code=lead_data.postal_code,
            country=lead_data.country,
            company_id=lead_data.company_id,
            created_by=str(current_user_id),
            created_at=datetime.now()
        )
        
        try:
            # Add to database
            self.db.add(new_lead)
            self.db.flush()  # Flush to get the ID without committing
            
            # Dispatch event
            self.event_dispatcher.dispatch(
                LeadCreatedEvent(
                    lead_id=new_lead.id,
                    lead_name=f"{new_lead.first_name} {new_lead.last_name}",
                    business_name=new_lead.business_name,
                    lead_source=new_lead.source.value,
                    lead_status=new_lead.status.value,
                    company_id=new_lead.company_id,
                    user_id=current_user_id
                )
            )
            
            # Commit changes
            self.db.commit()
            self.db.refresh(new_lead)
            
            return new_lead
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating lead: {str(e)}")
            raise
    
    # Read operations
    
    def get_lead_by_id(self, lead_id: str, company_id: UUID) -> Optional[Lead]:
        """Get a lead by ID and company ID"""
        return self.db.query(Lead).filter(
            and_(
                Lead.id == lead_id,
                Lead.company_id == company_id
            )
        ).first()
    
    def list_leads(self, 
                  company_id: UUID,
                  search_params: LeadSearchParams = None,
                  skip: int = 0, 
                  limit: int = 100) -> Tuple[List[Lead], int]:
        """
        List leads with optional filtering and pagination
        Returns tuple of (leads, total_count)
        """
        query = self.db.query(Lead).filter(Lead.company_id == company_id)
        
        # Apply filters if search_params is provided
        if search_params:
            if search_params.query:
                search_term = f"%{search_params.query}%"
                query = query.filter(
                    or_(
                        Lead.first_name.ilike(search_term),
                        Lead.last_name.ilike(search_term),
                        Lead.business_name.ilike(search_term),
                        Lead.email.ilike(search_term),
                        Lead.phone.ilike(search_term)
                    )
                )
            
            if search_params.status:
                query = query.filter(Lead.status == search_params.status)
            
            if search_params.source:
                query = query.filter(Lead.source == search_params.source)
            
            if search_params.sales_rep_id:
                query = query.filter(Lead.sales_rep_id == str(search_params.sales_rep_id))
            
            if search_params.created_after:
                query = query.filter(Lead.created_at >= search_params.created_after)
            
            if search_params.created_before:
                query = query.filter(Lead.created_at <= search_params.created_before)
            
            if search_params.min_lead_score is not None:
                query = query.filter(Lead.lead_score >= search_params.min_lead_score)
            
            if search_params.max_lead_score is not None:
                query = query.filter(Lead.lead_score <= search_params.max_lead_score)
            
            if search_params.industry:
                query = query.filter(Lead.industry == search_params.industry)
            
            # Handle sorting
            if search_params.sort_by:
                sort_column = getattr(Lead, search_params.sort_by, Lead.created_at)
                if search_params.sort_desc:
                    sort_column = desc(sort_column)
                else:
                    sort_column = asc(sort_column)
                query = query.order_by(sort_column)
            else:
                # Default sorting
                query = query.order_by(desc(Lead.created_at))
        else:
            # Default sorting if no search_params
            query = query.order_by(desc(Lead.created_at))
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        return query.all(), total_count
    
    # Update operations
    
    def update_lead(self, 
                   lead_id: str, 
                   company_id: UUID,
                   lead_data: LeadUpdate, 
                   current_user_id: UUID) -> Optional[Lead]:
        """Update an existing lead"""
        lead = self.get_lead_by_id(lead_id, company_id)
        
        if not lead:
            return None
        
        # Check if status is changing to dispatch proper event
        status_changing = lead_data.status is not None and lead.status != lead_data.status
        old_status = lead.status.value if status_changing else None
        
        # Update fields from the provided data
        for key, value in lead_data.dict(exclude_unset=True).items():
            setattr(lead, key, value)
        
        # Always update the updated_at and updated_by fields
        lead.updated_at = datetime.now()
        lead.updated_by = str(current_user_id)
        
        try:
            # Dispatch generic update event
            self.event_dispatcher.dispatch(
                LeadUpdatedEvent(
                    lead_id=lead.id,
                    lead_name=f"{lead.first_name} {lead.last_name}",
                    business_name=lead.business_name,
                    lead_source=lead.source.value,
                    lead_status=lead.status.value,
                    company_id=lead.company_id,
                    user_id=current_user_id
                )
            )
            
            # Dispatch status change event if applicable
            if status_changing:
                self.event_dispatcher.dispatch(
                    LeadStatusChangedEvent(
                        lead_id=lead.id,
                        lead_name=f"{lead.first_name} {lead.last_name}",
                        business_name=lead.business_name,
                        old_status=old_status,
                        new_status=lead.status.value,
                        company_id=lead.company_id,
                        user_id=current_user_id
                    )
                )
            
            # Commit changes
            self.db.commit()
            self.db.refresh(lead)
            
            return lead
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating lead: {str(e)}")
            raise
    
    def change_lead_status(self, 
                          lead_id: str, 
                          company_id: UUID,
                          new_status: LeadStatus, 
                          current_user_id: UUID) -> Optional[Lead]:
        """Change a lead's status"""
        lead = self.get_lead_by_id(lead_id, company_id)
        
        if not lead:
            return None
        
        old_status = lead.status.value
        
        # Only update if status is actually changing
        if lead.status != new_status:
            lead.status = new_status
            lead.updated_at = datetime.now()
            lead.updated_by = str(current_user_id)
            
            try:
                # Dispatch status change event
                self.event_dispatcher.dispatch(
                    LeadStatusChangedEvent(
                        lead_id=lead.id,
                        lead_name=f"{lead.first_name} {lead.last_name}",
                        business_name=lead.business_name,
                        old_status=old_status,
                        new_status=new_status.value,
                        company_id=lead.company_id,
                        user_id=current_user_id
                    )
                )
                
                # Commit changes
                self.db.commit()
                self.db.refresh(lead)
                
            except Exception as e:
                self.db.rollback()
                logger.error(f"Error changing lead status: {str(e)}")
                raise
        
        return lead
    
    def convert_lead_to_customer(self, 
                               lead_id: str, 
                               company_id: UUID, 
                               current_user_id: UUID) -> Dict[str, Any]:
        """Convert a lead to a customer"""
        lead = self.get_lead_by_id(lead_id, company_id)
        
        if not lead:
            return {"success": False, "message": "Lead not found"}
        
        # In a real implementation, this would create a Customer entity 
        # and transfer data from the lead
        # For now, we'll just mark the lead as converted
        lead.status = LeadStatus.CONVERTED
        lead.updated_at = datetime.now()
        lead.updated_by = str(current_user_id)
        
        try:
            # Dispatch lead converted event
            self.event_dispatcher.dispatch(
                LeadConvertedEvent(
                    lead_id=lead.id,
                    lead_name=f"{lead.first_name} {lead.last_name}",
                    business_name=lead.business_name,
                    company_id=lead.company_id,
                    user_id=current_user_id
                )
            )
            
            # Commit changes
            self.db.commit()
            
            return {
                "success": True, 
                "message": "Lead converted successfully", 
                "lead_id": lead.id
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error converting lead: {str(e)}")
            raise
    
    # Activity operations
    
    def add_lead_activity(self,
                         lead_id: str,
                         company_id: UUID,
                         activity_data: LeadActivity,
                         current_user_id: UUID) -> Optional[Activity]:
        """Add an activity to a lead"""
        lead = self.get_lead_by_id(lead_id, company_id)
        
        if not lead:
            return None
        
        # Create the activity
        activity = Activity(
            entity_type="LEAD",
            entity_id=lead_id,
            activity_type=activity_data.activity_type,
            subject=activity_data.subject,
            description=activity_data.description,
            assigned_to=str(activity_data.assigned_to) if activity_data.assigned_to else None,
            scheduled_date=activity_data.scheduled_date,
            due_date=activity_data.due_date,
            is_completed=activity_data.is_completed,
            status=ActivityStatus.COMPLETED if activity_data.is_completed else ActivityStatus.PENDING,
            company_id=company_id,
            created_by=str(current_user_id),
            created_at=datetime.now()
        )
        
        try:
            # Add to database
            self.db.add(activity)
            self.db.flush()
            
            # Dispatch activity added event
            self.event_dispatcher.dispatch(
                LeadActivityAddedEvent(
                    lead_id=lead.id,
                    lead_name=f"{lead.first_name} {lead.last_name}",
                    business_name=lead.business_name,
                    activity_id=activity.id,
                    activity_type=activity.activity_type.value,
                    activity_subject=activity.subject,
                    company_id=lead.company_id,
                    user_id=current_user_id
                )
            )
            
            # Commit changes
            self.db.commit()
            self.db.refresh(activity)
            
            return activity
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding lead activity: {str(e)}")
            raise
    
    def get_lead_activities(self,
                           lead_id: str,
                           company_id: UUID,
                           skip: int = 0,
                           limit: int = 100) -> Tuple[List[Activity], int]:
        """Get activities for a lead"""
        query = self.db.query(Activity).filter(
            and_(
                Activity.entity_type == "LEAD",
                Activity.entity_id == lead_id,
                Activity.company_id == company_id
            )
        ).order_by(desc(Activity.created_at))
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        return query.all(), total_count
    
    # Analytics operations
    
    def get_lead_analytics(self, company_id: UUID) -> Dict[str, Any]:
        """Get lead analytics data for a company"""
        # Calculate total leads by status
        status_counts = (
            self.db.query(
                Lead.status,
                func.count(Lead.id).label("count")
            )
            .filter(Lead.company_id == company_id)
            .group_by(Lead.status)
            .all()
        )
        
        # Calculate total leads by source
        source_counts = (
            self.db.query(
                Lead.source,
                func.count(Lead.id).label("count")
            )
            .filter(Lead.company_id == company_id)
            .group_by(Lead.source)
            .all()
        )
        
        # Conversion rates - would be calculated in a real implementation
        # Placeholder for demonstration
        
        return {
            "total_leads": sum(count for _, count in status_counts),
            "leads_by_status": {status.value: count for status, count in status_counts},
            "leads_by_source": {source.value: count for source, count in source_counts},
            "conversion_rate": 0.0,  # Placeholder
            "average_lead_score": 0.0  # Placeholder
        }

