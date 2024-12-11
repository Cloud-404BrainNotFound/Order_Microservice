from sqlalchemy import Column, String, Float, DateTime, Enum as SQLEnum
from app.database import Base
from datetime import datetime
import uuid
import enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class OrderStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    STRUNG = "strung"
    PICKED_UP = "picked_up"
    CANCELLED = "cancelled"

class StringingOrder(Base):
    __tablename__ = "orders"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # UUID for order ID
    sport = Column(String(50), nullable=False)  # Sport type (e.g., Tennis, Badminton)
    racket_model = Column(String(100), nullable=False)  # Racket model
    string = Column(String(100), nullable=False)  # String type
    tension = Column(String(20), nullable=False)  # Tension (e.g., 25 or 25x27)
    pickup_date = Column(DateTime, nullable=True)  # Desired pickup date
    notes = Column(String(1000), default="")  # Ensure the DB column allows 1000 chars
    price = Column(Float, nullable=False, default=0.0)  # Selected string price
    order_status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)  # Order status
    created_at = Column(DateTime, default=datetime.utcnow)  # Timestamp for order creation
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Timestamp for last update
    

class StringingOrderCreate(BaseModel):
    sport: str
    racket_model: str
    string: str
    tension: str
    pickup_date: datetime
    notes: Optional[str] = Field(default="", max_length=1000)  # Validation on 'notes'
    price: float

class UserOrder(Base):
    __tablename__ = "user_orders"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    order_id = Column(String(36), nullable=False, index=True)  # Remove ForeignKey
    created_at = Column(DateTime, default=datetime.utcnow)