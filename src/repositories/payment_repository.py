from fastapi import HTTPException
from sqlalchemy.orm import Session # type: ignore
from sqlalchemy import func # type: ignore
from rabbitmq.rabbitmq_producer import send_message
from uuid import UUID
from models.payment_model import Payment

class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_payment(self, reservation_id: UUID, amount: float, checkout_url: str, stripe_session_id: str, payment_intent_id: str):
        payment = Payment(
            reservation_id=reservation_id,
            amount=amount,
            checkout_url=checkout_url,
            stripe_session_id=stripe_session_id,
            payment_intent_id=payment_intent_id 
        )
        self.db.add(payment)
        self.db.commit()
        return payment
    
    def get_payments(self):
        return self.db.query(Payment).all()
    
    def get_payment(self, id: UUID):
        return self.db.query(Payment).filter(Payment.reservation_id == id).first()
    
    def cancel_payment(self, id: UUID):
        payment = self.get_payment(id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        self.db.delete(payment)
        self.db.commit()
        return payment