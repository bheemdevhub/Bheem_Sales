from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID, uuid4
from fastapi import HTTPException
from datetime import datetime
from app.modules.sales.core.models.sales_models import CustomerPayment
from app.modules.sales.core.schemas.customer_payment_schemas import CustomerPaymentCreate, CustomerPaymentUpdate

class CustomerPaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_payment(self, payment_data: CustomerPaymentCreate, current_user_id: UUID, company_id: UUID) -> CustomerPayment:
        try:
            payment = CustomerPayment(
                id=uuid4(),
                company_id=company_id,
                customer_id=payment_data.customer_id,
                invoice_id=payment_data.invoice_id,
                payment_reference=payment_data.payment_reference,
                payment_date=payment_data.payment_date,
                amount=payment_data.amount,
                currency_id=payment_data.currency_id,
                payment_method=payment_data.payment_method,
                status=payment_data.status,
                transaction_id=payment_data.transaction_id,
                bank_reference=payment_data.bank_reference,
                notes=payment_data.notes,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                created_by=current_user_id,
                updated_by=current_user_id
            )

            self.db.add(payment)
            await self.db.commit()
            await self.db.refresh(payment)
            return payment
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")



    async def list_payments(self, skip: int = 0, limit: int = 100) -> Tuple[List[CustomerPayment], int]:
        # Count total payments
        count_stmt = select(CustomerPayment)
        count_result = await self.db.execute(count_stmt)
        total = len(count_result.scalars().all())
        
        # Get paginated payments
        stmt = select(CustomerPayment).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        payments = result.scalars().all()
        return list(payments), total

    async def get_payment(self, payment_id: UUID) -> Optional[CustomerPayment]:
        stmt = select(CustomerPayment).where(CustomerPayment.id == payment_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_payment(self, payment_id: UUID, payment_data: CustomerPaymentUpdate) -> Optional[CustomerPayment]:
        payment = await self.get_payment(payment_id)
        if not payment:
            return None
        for key, value in payment_data.dict(exclude_unset=True).items():
            setattr(payment, key, value)
        await self.db.commit()
        await self.db.refresh(payment)
        return payment

    async def delete_payment(self, payment_id: UUID) -> bool:
        payment = await self.get_payment(payment_id)
        if not payment:
            return False
        await self.db.delete(payment)
        await self.db.commit()
        return True
