from repositories.payment_repository import PaymentRepository
from models.payment_model import Payment
from typing import List
from fastapi import HTTPException
from uuid import UUID

class PaymentService:
    def __init__(self, payment_repository: PaymentRepository):
        self.payment_repository = payment_repository
    
    def create_payment(self, reservation_id: UUID, amount: float):
        self.payment_repository.create_payment(reservation_id, amount)
        
    def get_payments(self):
        # Repository already has access to db through dependency injection
        return self.payment_repository.get_payments()
    
    def get_payment(self, id: UUID):
        payment = self.payment_repository.get_payment(id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        return payment
    
    def cancel_payment(self, id: UUID):
        payment = self.payment_repository.get_payment(id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        self.payment_repository.cancel_payment(id)