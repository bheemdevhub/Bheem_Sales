from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from app.modules.sales.core.models.sales_models import CustomerPayment
from app.modules.sales.core.schemas.customer_payment_schemas import CustomerPaymentCreate, CustomerPaymentUpdate

class CustomerPaymentService:
    def __init__(self, db: Session):
        self.db = db

    def create_payment(self, payment_data: CustomerPaymentCreate) -> CustomerPayment:
        payment = CustomerPayment(**payment_data.dict(), created_at=datetime.now())
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def list_payments(self, skip: int = 0, limit: int = 100) -> Tuple[List[CustomerPayment], int]:
        query = self.db.query(CustomerPayment)
        total = query.count()
        payments = query.offset(skip).limit(limit).all()
        return payments, total

    def get_payment(self, payment_id: UUID) -> Optional[CustomerPayment]:
        return self.db.query(CustomerPayment).filter(CustomerPayment.id == payment_id).first()

    def update_payment(self, payment_id: UUID, payment_data: CustomerPaymentUpdate) -> Optional[CustomerPayment]:
        payment = self.get_payment(payment_id)
        if not payment:
            return None
        for key, value in payment_data.dict(exclude_unset=True).items():
            setattr(payment, key, value)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def delete_payment(self, payment_id: UUID) -> bool:
        payment = self.get_payment(payment_id)
        if not payment:
            return False
        self.db.delete(payment)
        self.db.commit()
        return True
