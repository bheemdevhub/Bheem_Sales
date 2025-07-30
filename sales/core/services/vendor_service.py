from typing import List, Optional, Dict, Any, Union, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, desc, asc
import logging
from datetime import datetime, date
from uuid import UUID
import uuid

from bheem_core.modules.sales.core.models.sales_models import Vendor, CustomerType, CustomerStatus
from bheem_core.modules.sales.core.schemas.vendor_schemas import (
    VendorCreate, VendorUpdate, VendorSearchParams, VendorActivity
)
from bheem_core.modules.sales.events.vendor_events import (
    VendorEventDispatcher, VendorCreatedEvent, VendorUpdatedEvent, 
    VendorStatusChangedEvent, VendorActivityAddedEvent
)
from bheem_core.shared.models import Activity, ActivityType, ActivityStatus

logger = logging.getLogger(__name__)


class VendorService:
    """
    Service for managing vendor-related operations
    Handles CRUD operations, search, and business logic for vendors
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.event_dispatcher = VendorEventDispatcher()
    
    # Create operations
    
    def create_vendor(self, vendor_data: VendorCreate, current_user_id: UUID) -> Vendor:
        """Create a new vendor with basic information"""
        # Create a new ID (UUID)
        vendor_id = str(uuid.uuid4())
        
        # Create the new Vendor object
        new_vendor = Vendor(
            id=vendor_id,
            vendor_code=vendor_data.vendor_code,
            business_name=vendor_data.business_name,
            contact_name=vendor_data.contact_name,
            email=vendor_data.email,
            phone=vendor_data.phone,
            website=vendor_data.website,
            industry=vendor_data.industry,
            vendor_type=vendor_data.vendor_type,
            vendor_status=vendor_data.vendor_status,
            tax_id=vendor_data.tax_id,
            payment_terms=vendor_data.payment_terms,
            currency_id=vendor_data.currency_id,
            custom_fields=vendor_data.custom_fields or {},
            address_line1=vendor_data.address_line1,
            address_line2=vendor_data.address_line2,
            city=vendor_data.city,
            state=vendor_data.state,
            postal_code=vendor_data.postal_code,
            country=vendor_data.country,
            company_id=vendor_data.company_id,
            vendor_since=date.today(),
            created_by=str(current_user_id),
            created_at=datetime.now()
        )
        
        try:
            # Add to database
            self.db.add(new_vendor)
            self.db.flush()  # Flush to get the ID without committing
            
            # Dispatch event
            self.event_dispatcher.dispatch(
                VendorCreatedEvent(
                    vendor_id=new_vendor.id,
                    vendor_code=new_vendor.vendor_code,
                    business_name=new_vendor.business_name,
                    vendor_type=new_vendor.vendor_type.value,
                    company_id=new_vendor.company_id,
                    user_id=current_user_id
                )
            )
            
            # Commit changes
            self.db.commit()
            self.db.refresh(new_vendor)
            
            return new_vendor
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating vendor: {str(e)}")
            raise
    
    # Read operations
    
    def get_vendor_by_id(self, vendor_id: str, company_id: UUID) -> Optional[Vendor]:
        """Get a vendor by ID and company ID"""
        return self.db.query(Vendor).filter(
            and_(
                Vendor.id == vendor_id,
                Vendor.company_id == company_id
            )
        ).first()
    
    def get_vendor_by_code(self, vendor_code: str, company_id: UUID) -> Optional[Vendor]:
        """Get a vendor by code and company ID"""
        return self.db.query(Vendor).filter(
            and_(
                Vendor.vendor_code == vendor_code,
                Vendor.company_id == company_id
            )
        ).first()
    
    def list_vendors(self, 
                    company_id: UUID,
                    search_params: VendorSearchParams = None,
                    skip: int = 0, 
                    limit: int = 100) -> Tuple[List[Vendor], int]:
        """
        List vendors with optional filtering and pagination
        Returns tuple of (vendors, total_count)
        """
        query = self.db.query(Vendor).filter(Vendor.company_id == company_id)
        
        # Apply filters if search_params is provided
        if search_params:
            if search_params.query:
                search_term = f"%{search_params.query}%"
                query = query.filter(
                    or_(
                        Vendor.vendor_code.ilike(search_term),
                        Vendor.business_name.ilike(search_term),
                        Vendor.contact_name.ilike(search_term),
                        Vendor.email.ilike(search_term),
                        Vendor.phone.ilike(search_term)
                    )
                )
            
            if search_params.vendor_type:
                query = query.filter(Vendor.vendor_type == search_params.vendor_type)
            
            if search_params.vendor_status:
                query = query.filter(Vendor.vendor_status == search_params.vendor_status)
            
            if search_params.created_after:
                query = query.filter(Vendor.created_at >= search_params.created_after)
            
            if search_params.created_before:
                query = query.filter(Vendor.created_at <= search_params.created_before)
            
            if search_params.industry:
                query = query.filter(Vendor.industry == search_params.industry)
            
            # Handle sorting
            if search_params.sort_by:
                sort_column = getattr(Vendor, search_params.sort_by, Vendor.vendor_code)
                if search_params.sort_desc:
                    sort_column = desc(sort_column)
                else:
                    sort_column = asc(sort_column)
                query = query.order_by(sort_column)
            else:
                # Default sorting
                query = query.order_by(Vendor.vendor_code)
        else:
            # Default sorting if no search_params
            query = query.order_by(Vendor.vendor_code)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        return query.all(), total_count
    
    # Update operations
    
    def update_vendor(self, 
                     vendor_id: str, 
                     company_id: UUID,
                     vendor_data: VendorUpdate, 
                     current_user_id: UUID) -> Optional[Vendor]:
        """Update an existing vendor"""
        vendor = self.get_vendor_by_id(vendor_id, company_id)
        
        if not vendor:
            return None
        
        # Check if status is changing to dispatch proper event
        status_changing = vendor_data.vendor_status is not None and vendor.vendor_status != vendor_data.vendor_status
        old_status = vendor.vendor_status.value if status_changing else None
        
        # Update fields from the provided data
        for key, value in vendor_data.dict(exclude_unset=True).items():
            setattr(vendor, key, value)
        
        # Always update the updated_at and updated_by fields
        vendor.updated_at = datetime.now()
        vendor.updated_by = str(current_user_id)
        
        try:
            # Dispatch generic update event
            self.event_dispatcher.dispatch(
                VendorUpdatedEvent(
                    vendor_id=vendor.id,
                    vendor_code=vendor.vendor_code,
                    business_name=vendor.business_name,
                    vendor_type=vendor.vendor_type.value,
                    company_id=vendor.company_id,
                    user_id=current_user_id
                )
            )
            
            # Dispatch status change event if applicable
            if status_changing:
                self.event_dispatcher.dispatch(
                    VendorStatusChangedEvent(
                        vendor_id=vendor.id,
                        vendor_code=vendor.vendor_code,
                        business_name=vendor.business_name,
                        old_status=old_status,
                        new_status=vendor.vendor_status.value,
                        company_id=vendor.company_id,
                        user_id=current_user_id
                    )
                )
            
            # Commit changes
            self.db.commit()
            self.db.refresh(vendor)
            
            return vendor
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating vendor: {str(e)}")
            raise
    
    def change_vendor_status(self, 
                            vendor_id: str, 
                            company_id: UUID,
                            new_status: CustomerStatus, 
                            current_user_id: UUID) -> Optional[Vendor]:
        """Change a vendor's status"""
        vendor = self.get_vendor_by_id(vendor_id, company_id)
        
        if not vendor:
            return None
        
        old_status = vendor.vendor_status.value
        
        # Only update if status is actually changing
        if vendor.vendor_status != new_status:
            vendor.vendor_status = new_status
            vendor.updated_at = datetime.now()
            vendor.updated_by = str(current_user_id)
            
            try:
                # Dispatch status change event
                self.event_dispatcher.dispatch(
                    VendorStatusChangedEvent(
                        vendor_id=vendor.id,
                        vendor_code=vendor.vendor_code,
                        business_name=vendor.business_name,
                        old_status=old_status,
                        new_status=new_status.value,
                        company_id=vendor.company_id,
                        user_id=current_user_id
                    )
                )
                
                # Commit changes
                self.db.commit()
                self.db.refresh(vendor)
                
            except Exception as e:
                self.db.rollback()
                logger.error(f"Error changing vendor status: {str(e)}")
                raise
        
        return vendor
    
    # Activity operations
    
    def add_vendor_activity(self,
                           vendor_id: str,
                           company_id: UUID,
                           activity_data: VendorActivity,
                           current_user_id: UUID) -> Optional[Activity]:
        """Add an activity to a vendor"""
        vendor = self.get_vendor_by_id(vendor_id, company_id)
        
        if not vendor:
            return None
        
        # Create the activity
        activity = Activity(
            entity_type="VENDOR",
            entity_id=vendor_id,
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
                VendorActivityAddedEvent(
                    vendor_id=vendor.id,
                    vendor_code=vendor.vendor_code,
                    business_name=vendor.business_name,
                    activity_id=activity.id,
                    activity_type=activity.activity_type.value,
                    activity_subject=activity.subject,
                    company_id=vendor.company_id,
                    user_id=current_user_id
                )
            )
            
            # Commit changes
            self.db.commit()
            self.db.refresh(activity)
            
            return activity
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding vendor activity: {str(e)}")
            raise
    
    def get_vendor_activities(self,
                             vendor_id: str,
                             company_id: UUID,
                             skip: int = 0,
                             limit: int = 100) -> Tuple[List[Activity], int]:
        """Get activities for a vendor"""
        query = self.db.query(Activity).filter(
            and_(
                Activity.entity_type == "VENDOR",
                Activity.entity_id == vendor_id,
                Activity.company_id == company_id
            )
        ).order_by(desc(Activity.created_at))
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        return query.all(), total_count
    
    # Analytics operations
    
    def get_vendor_analytics(self, company_id: UUID) -> Dict[str, Any]:
        """Get analytics data for vendors"""
        # Calculate total vendors by status
        status_counts = (
            self.db.query(
                Vendor.vendor_status,
                func.count(Vendor.id).label("count")
            )
            .filter(Vendor.company_id == company_id)
            .group_by(Vendor.vendor_status)
            .all()
        )
        
        # Calculate total vendors by type
        type_counts = (
            self.db.query(
                Vendor.vendor_type,
                func.count(Vendor.id).label("count")
            )
            .filter(Vendor.company_id == company_id)
            .group_by(Vendor.vendor_type)
            .all()
        )
        
        return {
            "total_vendors": sum(count for _, count in status_counts),
            "vendors_by_status": {status.value: count for status, count in status_counts},
            "vendors_by_type": {vtype.value: count for vtype, count in type_counts},
        }

