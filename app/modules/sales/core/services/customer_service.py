
from typing import List, Optional, Dict, Any, Union, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, or_, and_, desc, asc
from fastapi import HTTPException
from uuid import uuid4, UUID
from datetime import datetime
from app.shared.models import Contact, Address, Tag
from app.modules.sales.core.models.sales_models import Customer
from app.shared.models import Person
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
import traceback
import logging

logger = logging.getLogger(__name__)

from app.modules.sales.core.schemas.customer_schemas import CustomerResponse


from app.modules.sales.core.models.sales_models import CustomerStatus
from app.modules.sales.events.customer_events import (
    CustomerUpdatedEvent,
    CustomerStatusChangedEvent,
    CustomerCreditLimitChangedEvent,
    CustomerActivityAddedEvent
)
from app.shared.models import Activity, ActivityStatus
from app.modules.sales.core.schemas.customer_schemas import CustomerActivity

class CustomerService:
    def __init__(self, db: AsyncSession):
        self.db = db
    


    async def create_customer(self, customer_data, current_user_id: UUID, company_id: UUID):
        try:
            # Check for duplicate customer_code in the same company
            existing_customer = await self.db.execute(
                select(Customer).where(
                    Customer.customer_code == customer_data.customer_code,
                    Customer.company_id == company_id
                )
            )
            if existing_customer.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Customer code already exists for this company")

            # Generate new UUID for Customer
            new_customer = Customer(
                id=uuid4(),
                person_type="customer",
                first_name=customer_data.first_name,
                last_name=customer_data.last_name,
                middle_name=getattr(customer_data, "middle_name", None),
                preferred_name=getattr(customer_data, "preferred_name", None),
                title=getattr(customer_data, "title", None),
                suffix=getattr(customer_data, "suffix", None),
                date_of_birth=getattr(customer_data, "date_of_birth", None),
                gender=getattr(customer_data, "gender", None),
                marital_status=getattr(customer_data, "marital_status", None),
                nationality=getattr(customer_data, "nationality", None),
                blood_group=getattr(customer_data, "blood_group", None),
                is_active=True,
                company_id=company_id,
                created_by=current_user_id,
                created_at=datetime.utcnow(),
                customer_code=customer_data.customer_code,
                business_name=customer_data.business_name,
                industry=customer_data.industry,
                customer_type=customer_data.customer_type,
                customer_status=customer_data.customer_status,
                tax_id=customer_data.tax_id,
                credit_limit=customer_data.credit_limit,
                payment_terms=customer_data.payment_terms,
                currency_id=customer_data.currency_id,
                sales_rep_id=customer_data.sales_rep_id,
                preferred_communication=customer_data.preferred_communication,
                custom_fields=customer_data.custom_fields or {}
            )
            self.db.add(new_customer)
            await self.db.flush()
            person_id = new_customer.id

            # Create Contacts
            if hasattr(customer_data, "contacts") and customer_data.contacts:
                for contact_data in customer_data.contacts:
                    contact = Contact(
                        person_id=person_id,
                        email_primary=contact_data.email_primary,
                        phone_primary=getattr(contact_data, "phone_primary", None),
                        phone_mobile=getattr(contact_data, "phone_mobile", None),
                        is_active=contact_data.is_active
                    )
                    self.db.add(contact)

            # Create Addresses
            if hasattr(customer_data, "addresses") and customer_data.addresses:
                for addr in customer_data.addresses:
                    address = Address(
                        entity_id=person_id,
                        entity_type="CUSTOMER",
                        address_type=addr.address_type,
                        line1=addr.line1,
                        line2=getattr(addr, "line2", None),
                        city=addr.city,
                        state=addr.state,
                        postal_code=addr.postal_code,
                        country=addr.country,
                        is_active=addr.is_active
                    )
                    self.db.add(address)

            # Create Tags
            if hasattr(customer_data, "tags") and customer_data.tags:
                for tag_value in customer_data.tags:
                    tag = Tag(
                        entity_type="CUSTOMER",
                        entity_id=person_id,
                        tag_value=tag_value,
                        company_id=company_id,
                        applied_by=person_id,  # use newly created customer's ID
                        applied_date=datetime.utcnow(),
                        is_active=True
                    )
                    self.db.add(tag)

            await self.db.flush()
            await self.db.commit()

            # Eagerly reload customer with related data to avoid DetachedInstanceError & MissingGreenlet
            result = await self.db.execute(
                select(Customer)
                .options(
                    selectinload(Customer.contacts),
                    selectinload(Customer.addresses),
                    selectinload(Customer.tags),
                    selectinload(Customer.bank_accounts),
                    selectinload(Customer.passports)
                )
                .where(Customer.id == person_id)
            )
            loaded_customer = result.scalar_one()

            # Prepare output with tag values
            return CustomerResponse.model_validate(
                {
                    **loaded_customer.__dict__,
                    "tags": [tag.tag_value for tag in loaded_customer.tags]
                },
                from_attributes=True
            )

        except Exception:
            await self.db.rollback()
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Unexpected error while creating customer")

