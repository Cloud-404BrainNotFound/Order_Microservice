from sqlalchemy import Column, String, Float, Integer, Enum as SQLEnum, DateTime, JSON, Boolean
from app.database import Base
from datetime import datetime
import uuid
import enum

class OrderStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String(36), nullable=False)
    product_id = Column(String(36), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Float, nullable=False, default=0.0)
    subtotal = Column(Float, nullable=False, default=0.0)
    extra = Column(JSON, default={})

class Order(Base):
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False)
    store_id = Column(String(36), nullable=False)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    total_amount = Column(Float, nullable=False, default=0.0)
    shipping_address = Column(String(500), default="")
    billing_address = Column(String(500), default="")
    payment_id = Column(String(36), default="")
    notes = Column(String(1000), default="")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    extra = Column(JSON, default={})