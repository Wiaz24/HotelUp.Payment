from pydantic import BaseModel, Field # type: ignore
from datetime import datetime
from typing import Optional
from uuid import UUID
   
class PaymentBase(BaseModel):
    id: UUID
    reservation_id: UUID
    amount: float
    checkout_url: Optional[str]
    stripe_session_id: Optional[str]
    created_at: datetime
    is_paid: bool
    payment_intent_id: Optional[str]

    class Config:
        from_attributes = True

class PaymentURL(BaseModel):
    checkout_url: str
    
class Config:
    from_attributes = True