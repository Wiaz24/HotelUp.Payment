from enum import Enum
from uuid import uuid4
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Enum as SqlEnum # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore
from sqlalchemy.dialects.postgresql import UUID as SqlUUID # type: ignore
from datetime import datetime
from sqlalchemy import ForeignKey # type: ignore
from sqlalchemy.orm import relationship # type: ignore
from models.base_model import Base

class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = {'schema': 'payment'}
    
    id = Column(SqlUUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    reservation_id = Column(SqlUUID(as_uuid=True), nullable=False)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_paid = Column(Boolean, default=False)
    checkout_url = Column(String, nullable=True)
    stripe_session_id = Column(String, nullable=True)
    payment_intent_id = Column(String, nullable=True)
    