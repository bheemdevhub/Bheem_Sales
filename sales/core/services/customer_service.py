from typing import List, Optional, Dict, Any, Union, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, desc, asc
import logging
from datetime import datetime, date
from uuid import UUID
import uuid

from bheem_core.modules.sales.core.models.sales_models import Customer, CustomerType, CustomerStatus
from bheem_core.modules.sales.core.schemas.customer_schemas import (
    CustomerCreate, CustomerUpdate, CustomerSearchParams, 
    CustomerActivity
)
from bheem_core.modules.sales.events.customer_events import (
    CustomerEventDispatcher, CustomerCreatedEvent, CustomerUpdatedEvent, 
    CustomerStatusChangedEvent, CustomerCreditLimitChangedEvent,
    CustomerActivityAddedEvent
)
from bheem_core.shared.models import Activity, ActivityType, ActivityStatus

logger = logging.getLogger(__name__)


class CustomerService:
    """
    Service for managing customer-related operations
    Handles CRUD operations, search, and business logic for customers
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.event_dispatcher = CustomerEventDispatcher()
    
    # Create operations
    
    def create_customer(self, customer_data: CustomerCreate, current_user_id: UUID, company_id: UUID) -> Customer:
        from bheem_core.shared.models import Person, Contact, Address, BankAccount, Passport
        import uuid
        person_id = str(uuid.uuid4())

        # Extract nested arrays or default to empty
        contacts_data = getattr(customer_data, "contacts", []) or []
        addresses_data = getattr(customer_data, "addresses", []) or []
        bank_accounts_data = getattr(customer_data, "bank_accounts", []) or []
        passports_data = getattr(customer_data, "passports", []) or []

        # Prepare Person fields (demographic and basic info)
        person_fields = [
            "first_name", "last_name", "date_of_birth", "gender", "profile_image_url"
        ]
        person_dict = {k: getattr(customer_data, k, None) for k in person_fields if hasattr(customer_data, k)}
        person_dict.update({
            "id": person_id,
            "person_type": "customer",
            "is_active": True,
            "company_id": company_id
        })
        person = Person(**person_dict)

        # Prepare Customer fields (extension)
        customer_fields = [
            "customer_code", "business_name", "industry", "customer_type", "customer_status",
            "tax_id", "credit_limit", "payment_terms", "currency_id", "sales_rep_id",
            "preferred_communication", "custom_fields"
        ]
        customer_dict = {k: getattr(customer_data, k, None) for k in customer_fields if hasattr(customer_data, k)}
        customer_dict.update({
            "id": person_id,
            "company_id": company_id,
            "created_at": datetime.now()
        })
        # Do NOT pass tags, contacts, addresses, bank_accounts, passports directly to Customer
        customer = Customer(**customer_dict)

        try:
            self.db.add(person)
            self.db.add(customer)
            self.db.flush()

            # Create contacts
            for contact in contacts_data:
                contact_obj = Contact(person_id=person_id, **contact)
                self.db.add(contact_obj)

            # Create addresses
            for address in addresses_data:
                address_obj = Address(
                    entity_type="CUSTOMER",
                    entity_id=person_id,
                    **address
                )
                self.db.add(address_obj)

            # Create bank accounts
            for bank in bank_accounts_data:
                bank_obj = BankAccount(person_id=person_id, **bank)
                self.db.add(bank_obj)

            # Create passports
            for passport in passports_data:
                passport_obj = Passport(person_id=person_id, **passport)
                self.db.add(passport_obj)

            self.db.commit()
            self.db.refresh(customer)
            return customer
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating customer: {e}")
            raise HTTPException(status_code=500, detail="Failed to create customer")
    
    # Read operations
    
    def get_customer_by_id(self, customer_id: str, company_id: UUID) -> Optional[dict]:
        """Get a customer by ID and company ID, joined with Person and related tables"""
        from bheem_core.shared.models import Person, Contact, Address, BankAccount, Passport
        customer = self.db.query(Customer).filter(
            and_(
                Customer.id == customer_id,
                Customer.company_id == company_id
            )
        ).first()
        if not customer:
            return None
        person = self.db.query(Person).filter(Person.id == customer_id).first()
        contacts = self.db.query(Contact).filter(Contact.person_id == customer_id).all()
        addresses = self.db.query(Address).filter(Address.entity_id == customer_id, Address.entity_type == "CUSTOMER").all()
        bank_accounts = self.db.query(BankAccount).filter(BankAccount.person_id == customer_id).all()
        passports = self.db.query(Passport).filter(Passport.person_id == customer_id).all()

        # Merge fields from both models
        response = {
            # Customer fields
            "id": customer.id,
            "customer_code": customer.customer_code,
            "business_name": customer.business_name,
            "industry": customer.industry,
            "customer_type": customer.customer_type,
            "customer_status": customer.customer_status,
            "tax_id": customer.tax_id,
            "credit_limit": float(customer.credit_limit) if customer.credit_limit is not None else 0.0,
            "payment_terms": customer.payment_terms,
            "currency_id": customer.currency_id,
            "sales_rep_id": customer.sales_rep_id,
            "preferred_communication": customer.preferred_communication,
            "tags": customer.tags or [],
            "custom_fields": customer.custom_fields or {},
            "company_id": customer.company_id,
            "customer_since": getattr(customer, "customer_since", None),
            "last_purchase_date": getattr(customer, "last_purchase_date", None),
            "created_at": customer.created_at,
            "updated_at": customer.updated_at,
            # Person fields
            "first_name": getattr(person, "first_name", None),
            "last_name": getattr(person, "last_name", None),
            "middle_name": getattr(person, "middle_name", None),
            "preferred_name": getattr(person, "preferred_name", None),
            "title": getattr(person, "title", None),
            "suffix": getattr(person, "suffix", None),
            "date_of_birth": getattr(person, "date_of_birth", None),
            "gender": getattr(person, "gender", None),
            "marital_status": getattr(person, "marital_status", None),
            "nationality": getattr(person, "nationality", None),
            "blood_group": getattr(person, "blood_group", None),
            "is_active": getattr(person, "is_active", None),
            # Related tables
            "contacts": [c.__dict__ for c in contacts],
            "addresses": [a.__dict__ for a in addresses],
            "bank_accounts": [b.__dict__ for b in bank_accounts],
            "passports": [p.__dict__ for p in passports],
        }
        # Remove SQLAlchemy internal state from related objects
        for rel in ["contacts", "addresses", "bank_accounts", "passports"]:
            for obj in response[rel]:
                obj.pop("_sa_instance_state", None)
        return response
    
    def get_customer_by_code(self, customer_code: str, company_id: UUID) -> Optional[Customer]:
        """Get a customer by code and company ID"""
        return self.db.query(Customer).filter(
            and_(
                Customer.customer_code == customer_code,
                Customer.company_id == company_id
            )
        ).first()
    
    def list_customers(self, 
                      company_id: UUID,
                      search_params: CustomerSearchParams = None,
                      skip: int = 0, 
                      limit: int = 100) -> Tuple[List[Customer], int]:
        """
        List customers with optional filtering and pagination
        Returns tuple of (customers, total_count)
        """
        query = self.db.query(Customer).filter(Customer.company_id == company_id)
        
        # Apply filters if search_params is provided
        if search_params:
            if search_params.query:
                search_term = f"%{search_params.query}%"
                query = query.filter(
                    or_(
                        Customer.customer_code.ilike(search_term),
                        Customer.first_name.ilike(search_term),
                        Customer.last_name.ilike(search_term),
                        Customer.business_name.ilike(search_term),
                        Customer.email.ilike(search_term),
                        Customer.phone.ilike(search_term)
                    )
                )
            
            if search_params.customer_type:
                query = query.filter(Customer.customer_type == search_params.customer_type)
            
            if search_params.customer_status:
                query = query.filter(Customer.customer_status == search_params.customer_status)
            
            if search_params.sales_rep_id:
                query = query.filter(Customer.sales_rep_id == str(search_params.sales_rep_id))
            
            if search_params.created_after:
                query = query.filter(Customer.created_at >= search_params.created_after)
            
            if search_params.created_before:
                query = query.filter(Customer.created_at <= search_params.created_before)
            
            if search_params.min_credit_limit is not None:
                query = query.filter(Customer.credit_limit >= search_params.min_credit_limit)
            
            if search_params.max_credit_limit is not None:
                query = query.filter(Customer.credit_limit <= search_params.max_credit_limit)
            
            if search_params.industry:
                query = query.filter(Customer.industry == search_params.industry)
            
            # Handle sorting
            if search_params.sort_by:
                sort_column = getattr(Customer, search_params.sort_by, Customer.customer_code)
                if search_params.sort_desc:
                    sort_column = desc(sort_column)
                else:
                    sort_column = asc(sort_column)
                query = query.order_by(sort_column)
            else:
                # Default sorting
                query = query.order_by(Customer.customer_code)
        else:
            # Default sorting if no search_params
            query = query.order_by(Customer.customer_code)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        return query.all(), total_count
    
    # Update operations
    
    def update_customer(self, 
                       customer_id: str, 
                       company_id: UUID,
                       customer_data: CustomerUpdate, 
                       current_user_id: UUID) -> Optional[Customer]:
        """Update an existing customer"""
        customer = self.get_customer_by_id(customer_id, company_id)
        
        if not customer:
            return None
        
        # Check if status is changing to dispatch proper event
        status_changing = customer_data.customer_status is not None and customer.customer_status != customer_data.customer_status
        old_status = customer.customer_status.value if status_changing else None
        
        # Check if credit limit is changing to dispatch proper event
        credit_limit_changing = customer_data.credit_limit is not None and customer.credit_limit != customer_data.credit_limit
        old_credit_limit = float(customer.credit_limit) if credit_limit_changing else None
        
        # Update fields from the provided data
        for key, value in customer_data.dict(exclude_unset=True).items():
            setattr(customer, key, value)
        
        # Always update the updated_at and updated_by fields
        customer.updated_at = datetime.now()
        customer.updated_by = str(current_user_id)
        
        try:
            # Dispatch generic update event
            self.event_dispatcher.dispatch(
                CustomerUpdatedEvent(
                    customer_id=customer.id,
                    customer_code=customer.customer_code,
                    display_name=customer.display_name,
                    customer_type=customer.customer_type.value,
                    company_id=customer.company_id,
                    user_id=current_user_id
                )
            )
            
            # Dispatch status change event if applicable
            if status_changing:
                self.event_dispatcher.dispatch(
                    CustomerStatusChangedEvent(
                        customer_id=customer.id,
                        customer_code=customer.customer_code,
                        display_name=customer.display_name,
                        old_status=old_status,
                        new_status=customer.customer_status.value,
                        company_id=customer.company_id,
                        user_id=current_user_id
                    )
                )
            
            # Dispatch credit limit change event if applicable
            if credit_limit_changing:
                self.event_dispatcher.dispatch(
                    CustomerCreditLimitChangedEvent(
                        customer_id=customer.id,
                        customer_code=customer.customer_code,
                        display_name=customer.display_name,
                        old_credit_limit=old_credit_limit,
                        new_credit_limit=float(customer.credit_limit),
                        company_id=customer.company_id,
                        user_id=current_user_id
                    )
                )
            
            # Commit changes
            self.db.commit()
            self.db.refresh(customer)
            
            return customer
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating customer: {str(e)}")
            raise
    
    def change_customer_status(self, 
                              customer_id: str, 
                              company_id: UUID,
                              new_status: CustomerStatus, 
                              current_user_id: UUID) -> Optional[Customer]:
        """Change a customer's status"""
        customer = self.get_customer_by_id(customer_id, company_id)
        
        if not customer:
            return None
        
        old_status = customer.customer_status.value
        
        # Only update if status is actually changing
        if customer.customer_status != new_status:
            customer.customer_status = new_status
            customer.updated_at = datetime.now()
            customer.updated_by = str(current_user_id)
            
            try:
                # Dispatch status change event
                self.event_dispatcher.dispatch(
                    CustomerStatusChangedEvent(
                        customer_id=customer.id,
                        customer_code=customer.customer_code,
                        display_name=customer.display_name,
                        old_status=old_status,
                        new_status=new_status.value,
                        company_id=customer.company_id,
                        user_id=current_user_id
                    )
                )
                
                # Commit changes
                self.db.commit()
                self.db.refresh(customer)
                
            except Exception as e:
                self.db.rollback()
                logger.error(f"Error changing customer status: {str(e)}")
                raise
        
        return customer
    
    # Activity operations
    
    def add_customer_activity(self,
                             customer_id: str,
                             company_id: UUID,
                             activity_data: CustomerActivity,
                             current_user_id: UUID) -> Optional[Activity]:
        """Add an activity to a customer"""
        customer = self.get_customer_by_id(customer_id, company_id)
        
        if not customer:
            return None
        
        # Create the activity
        activity = Activity(
            entity_type="CUSTOMER",
            entity_id=customer_id,
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
                CustomerActivityAddedEvent(
                    customer_id=customer.id,
                    customer_code=customer.customer_code,
                    display_name=customer.display_name,
                    activity_id=activity.id,
                    activity_type=activity.activity_type.value,
                    activity_subject=activity.subject,
                    company_id=customer.company_id,
                    user_id=current_user_id
                )
            )
            
            # Commit changes
            self.db.commit()
            self.db.refresh(activity)
            
            return activity
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding customer activity: {str(e)}")
            raise
    
    def get_customer_activities(self,
                               customer_id: str,
                               company_id: UUID,
                               skip: int = 0,
                               limit: int = 100) -> Tuple[List[Activity], int]:
        """Get activities for a customer"""
        query = self.db.query(Activity).filter(
            and_(
                Activity.entity_type == "CUSTOMER",
                Activity.entity_id == customer_id,
                Activity.company_id == company_id
            )
        ).order_by(desc(Activity.created_at))
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        return query.all(), total_count
    
    # Analytics operations
    
    def get_customer_analytics(self, customer_id: str, company_id: UUID) -> Dict[str, Any]:
        """Get analytics data for a customer"""
        customer = self.get_customer_by_id(customer_id, company_id)
        
        if not customer:
            return {}
        
        # This would typically involve more complex queries to various tables
        # For now, return a simple placeholder structure
        return {
            "customer_id": customer.id,
            "total_orders": 0,  # Would be calculated from orders table
            "total_invoiced": 0.0,  # Would be calculated from invoices table
            "total_paid": 0.0,  # Would be calculated from payments table
            "last_purchase_date": None,  # Would be calculated from orders table
            "average_order_value": 0.0,  # Would be calculated from orders table
            "purchase_frequency": 0.0,  # Would be calculated from orders table
            "customer_lifetime_value": 0.0,  # Would be calculated from multiple tables
            "payment_performance": 0.0  # Would be calculated from invoices/payments table
        }

