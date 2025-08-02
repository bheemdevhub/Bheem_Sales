from typing import List, Optional, Dict, Any, Union, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, or_, and_, desc, asc, select
import logging
from datetime import datetime, date
from uuid import UUID,uuid4
from app.shared.models import Contact
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.modules.sales.core.models.sales_models import Lead, LeadStatus, Tag
from app.modules.sales.core.schemas.lead_schemas import (
    LeadCreate, LeadUpdate, LeadSearchParams, LeadActivity
)
from app.modules.sales.events.lead_events import (
    LeadEventDispatcher, LeadCreatedEvent, LeadUpdatedEvent, 
    LeadStatusChangedEvent, LeadConvertedEvent, LeadActivityAddedEvent
)
from app.shared.models import Activity, ActivityType, ActivityStatus

logger = logging.getLogger(__name__)


class LeadService:
    """
    Service for managing lead-related operations
    Handles CRUD operations, search, conversion, and business logic for leads
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Create operations
    
    async def create_lead(self, lead_data, current_user_id: UUID, company_id: UUID):
        try:
            lead_id = uuid4()

            # Separate contact data
            contact_data = {}
            if getattr(lead_data, "email", None):
                contact_data["email_primary"] = lead_data.email
            if getattr(lead_data, "phone", None):
                contact_data["phone_primary"] = lead_data.phone

            # Extract tags as string list
            tag_names = lead_data.tags or []
            lead_dict = lead_data.model_dump(exclude={"email", "phone", "tags"})

            # Create Lead
            new_lead = Lead(
                id=lead_id,
                **lead_dict,
                created_by=current_user_id,
                updated_by=current_user_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            self.db.add(new_lead)

            # Create Contact (optional)
            if contact_data:
                contact = Contact(
                    person_id=lead_id,
                    **contact_data
                )
                self.db.add(contact)

            # Create Tag objects and associate
            tag_objs = []
            for name in tag_names:
                stmt = select(Tag).where(
                    Tag.tag_value == name,
                    Tag.company_id == company_id,
                    Tag.entity_type == "lead",
                    Tag.entity_id == lead_id,
                )
                result = await self.db.execute(stmt)
                tag = result.scalar_one_or_none()

                if not tag:
                    tag = Tag(
                        id=uuid4(),
                        name=name,
                        company_id=company_id,
                        applied_by=current_user_id,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                    )
                    self.db.add(tag)
                    await self.db.flush()  # So we can use tag object immediately

                tag_objs.append(tag)

            new_lead.tags = tag_objs

            await self.db.commit()
            await self.db.refresh(new_lead)
            return new_lead

        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail="Lead creation failed due to database constraint.")
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    # Read operations
    
    async def get_lead_by_id(self, lead_id: str, company_id: UUID) -> Optional[Lead]:
        """Get a lead by ID and company ID"""
        stmt = select(Lead).filter(
            and_(
                Lead.id == lead_id,
                Lead.company_id == company_id
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_leads(self, 
                  company_id: UUID,
                  search_params: LeadSearchParams = None,
                  skip: int = 0, 
                  limit: int = 100) -> Tuple[List[Lead], int]:
        """
        List leads with optional filtering and pagination
        Returns tuple of (leads, total_count)
        """
        stmt = select(Lead).filter(Lead.company_id == company_id)
        
        # Apply filters if search_params is provided
        if search_params:
            if search_params.query:
                search_term = f"%{search_params.query}%"
                stmt = stmt.filter(
                    or_(
                        Lead.first_name.ilike(search_term),
                        Lead.last_name.ilike(search_term),
                        Lead.business_name.ilike(search_term),
                        Lead.email.ilike(search_term),
                        Lead.phone.ilike(search_term)
                    )
                )
            
            if search_params.status:
                stmt = stmt.filter(Lead.status == search_params.status)
            
            if search_params.source:
                stmt = stmt.filter(Lead.source == search_params.source)
            
            if search_params.sales_rep_id:
                stmt = stmt.filter(Lead.sales_rep_id == str(search_params.sales_rep_id))
            
            if search_params.created_after:
                stmt = stmt.filter(Lead.created_at >= search_params.created_after)
            
            if search_params.created_before:
                stmt = stmt.filter(Lead.created_at <= search_params.created_before)
            
            if search_params.min_lead_score is not None:
                stmt = stmt.filter(Lead.lead_score >= search_params.min_lead_score)
            
            if search_params.max_lead_score is not None:
                stmt = stmt.filter(Lead.lead_score <= search_params.max_lead_score)
            
            if search_params.industry:
                stmt = stmt.filter(Lead.industry == search_params.industry)
            
            # Handle sorting
            if search_params.sort_by:
                sort_column = getattr(Lead, search_params.sort_by, Lead.created_at)
                if search_params.sort_desc:
                    sort_column = desc(sort_column)
                else:
                    sort_column = asc(sort_column)
                stmt = stmt.order_by(sort_column)
            else:
                # Default sorting
                stmt = stmt.order_by(desc(Lead.created_at))
        else:
            # Default sorting if no search_params
            stmt = stmt.order_by(desc(Lead.created_at))
        
        # Get total count before pagination
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.db.execute(count_stmt)
        total_count = count_result.scalar()
        
        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)
        
        result = await self.db.execute(stmt)
        leads = result.scalars().all()
        
        return leads, total_count
    
    # Update operations
    
    async def update_lead(self, 
                   lead_id: str, 
                   company_id: UUID,
                   lead_data: LeadUpdate, 
                   current_user_id: UUID) -> Optional[Lead]:
        """Update an existing lead"""
        lead = await self.get_lead_by_id(lead_id, company_id)
        
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
            await self.db.commit()
            await self.db.refresh(lead)
            
            return lead
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating lead: {str(e)}")
            raise
    
    async def change_lead_status(self, 
                          lead_id: str, 
                          company_id: UUID,
                          new_status: LeadStatus, 
                          current_user_id: UUID) -> Optional[Lead]:
        """Change a lead's status"""
        lead = await self.get_lead_by_id(lead_id, company_id)
        
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
                await self.db.commit()
                await self.db.refresh(lead)
                
            except Exception as e:
                await self.db.rollback()
                logger.error(f"Error changing lead status: {str(e)}")
                raise
        
        return lead
    
    async def convert_lead_to_customer(self, 
                               lead_id: str, 
                               company_id: UUID, 
                               current_user_id: UUID) -> Dict[str, Any]:
        """Convert a lead to a customer"""
        lead = await self.get_lead_by_id(lead_id, company_id)
        
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
            await self.db.commit()
            
            return {
                "success": True, 
                "message": "Lead converted successfully", 
                "lead_id": lead.id
            }
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error converting lead: {str(e)}")
            raise
    
    # Activity operations
    
    async def add_lead_activity(self,
                         lead_id: str,
                         company_id: UUID,
                         activity_data: LeadActivity,
                         current_user_id: UUID) -> Optional[Activity]:
        """Add an activity to a lead"""
        lead = await self.get_lead_by_id(lead_id, company_id)
        
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
            await self.db.flush()
            
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
            await self.db.commit()
            await self.db.refresh(activity)
            
            return activity
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error adding lead activity: {str(e)}")
            raise
    
    async def get_lead_activities(self,
                           lead_id: str,
                           company_id: UUID,
                           skip: int = 0,
                           limit: int = 100) -> Tuple[List[Activity], int]:
        """Get activities for a lead"""
        stmt = select(Activity).filter(
            and_(
                Activity.entity_type == "LEAD",
                Activity.entity_id == lead_id,
                Activity.company_id == company_id
            )
        ).order_by(desc(Activity.created_at))
        
        # Get total count before pagination
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.db.execute(count_stmt)
        total_count = count_result.scalar()
        
        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)
        
        result = await self.db.execute(stmt)
        activities = result.scalars().all()
        
        return activities, total_count
    
    # Analytics operations
    
    async def get_lead_analytics(self, company_id: UUID) -> Dict[str, Any]:
        """Get lead analytics data for a company"""
        # Calculate total leads by status
        status_stmt = select(
            Lead.status,
            func.count(Lead.id).label("count")
        ).filter(Lead.company_id == company_id).group_by(Lead.status)
        
        status_result = await self.db.execute(status_stmt)
        status_counts = status_result.all()
        
        # Calculate total leads by source
        source_stmt = select(
            Lead.source,
            func.count(Lead.id).label("count")
        ).filter(Lead.company_id == company_id).group_by(Lead.source)
        
        source_result = await self.db.execute(source_stmt)
        source_counts = source_result.all()
        
        # Conversion rates - would be calculated in a real implementation
        # Placeholder for demonstration
        
        return {
            "total_leads": sum(count for _, count in status_counts),
            "leads_by_status": {status.value: count for status, count in status_counts},
            "leads_by_source": {source.value: count for source, count in source_counts},
            "conversion_rate": 0.0,  # Placeholder
            "average_lead_score": 0.0  # Placeholder
        }
