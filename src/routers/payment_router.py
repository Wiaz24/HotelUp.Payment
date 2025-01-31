from typing import Annotated, List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from jose import JWTError, jwt
from uuid import UUID
import stripe
from env import settings
from schemas.payment import PaymentBase, PaymentURL
from models.payment_model import Payment
from services.payment_service import PaymentService
from repositories.payment_repository import PaymentRepository

router = APIRouter()

router = APIRouter(
    prefix="/api/payment",
    tags=["Payment"],
)

stripe.api_key = settings.STRIPE_API_KEY

# @router.post("/create-checkout-session")
# async def create_checkout_session(data: PaymentBase, db: Session = Depends(get_db)):
#     try:
#         if data.amount == 0.0:  # Fixed typo in amount
#             raise HTTPException(status_code=400, detail="The amount cannot be 0")

#         session = stripe.checkout.Session.create(
#             payment_method_types=["card"],
#             line_items=[{
#                 "price_data": {
#                     "currency": "pln",
#                     "unit_amount": int(data.amount * 100),  # Convert to cents
#                     "product_data": {
#                         "name": f"Rezerwacja nr: {data.reservation_id}",
#                     },
#                 },
#                 "quantity": 1
#             }],
#             mode="payment",
#             success_url="https://localhost",
#             cancel_url="https://localhost",
#         )

#         # Save payment to database
#         payment_repository = PaymentRepository(db)
#         payment_service = PaymentService(payment_repository)
#         payment_service.create_payment(data)

#         return {"checkout_url": session.url}
#     except Exception as e:
#         raise HTTPException(status_code=403, detail=str(e))
    
@router.get("/get-payments", response_model=List[PaymentBase])
async def get_payments(db: Session = Depends(get_db)):
    payment_repository = PaymentRepository(db)
    payment_service = PaymentService(payment_repository)
    return payment_service.get_payments()

@router.get("/get-payment/{reservation_id}", response_model=PaymentURL)
async def get_payment(reservation_id: UUID, db: Session = Depends(get_db)):
    payment_repository = PaymentRepository(db)
    payment_service = PaymentService(payment_repository)
    return payment_service.get_payment(reservation_id)

@router.get("/cancel-payment/{reservation_id}")
async def cancel_payment(reservation_id: UUID, db: Session = Depends(get_db)):
    payment_repository = PaymentRepository(db)
    payment_service = PaymentService(payment_repository)
    return payment_service.cancel_payment(reservation_id)