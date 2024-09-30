from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.order import Order
from app.database import get_db
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from typing import List
import enum

order_router = APIRouter()
class OrderStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
class UserPaymentRequest(BaseModel):
    user_id: str
class OrderCreate(BaseModel):
    user_id: str
    store_id: str
    total_amount: float
    shipping_address: str
    billing_address: str
    status: Optional[str] = "PENDING"  # 设置默认状态为 "pending"
    notes: Optional[str] = ""

@order_router.post("/add_order", response_model=dict)
def add_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    new_order = Order(
        user_id=order_data.user_id,
        store_id=order_data.store_id,
        total_amount=order_data.total_amount,
        shipping_address=order_data.shipping_address,
        billing_address=order_data.billing_address,
        notes=order_data.notes,
        status=order_data.status,  # 默认为 pending 状态
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(new_order)
    db.commit()
    return {"message": "Order created successfully", "order_id": new_order.id}

@order_router.get("/get_order/{order_id}", response_model=dict)
def get_order(order_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {
        "order_id": order.id,
        "user_id": order.user_id,
        "store_id": order.store_id,
        "total_amount": order.total_amount,
        "shipping_address": order.shipping_address,
        "billing_address": order.billing_address,
        "status": order.status.value,
        "notes": order.notes,
        "created_at": order.created_at,
        "updated_at": order.updated_at
    }

class UpdateOrderStatusRequest(BaseModel):
    order_id: str
    status: str

@order_router.post("/update_order_status", response_model=dict)
def update_order_status(request: UpdateOrderStatusRequest, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == request.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = request.status
    order.updated_at = datetime.now()
    db.commit()
    return {"message": "Order status updated successfully", "order_id": order.id, "status": order.status.value}

@order_router.post("/search_orders_by_user")
def get_orders_by_user(request: UserPaymentRequest, db: Session = Depends(get_db)) -> List[dict]:
    user_id = request.user_id
    orders = db.query(Order).filter(Order.user_id == user_id).all()
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for this user")
    return [
        {
            "order_id": order.id,
            "user_id": order.user_id,
            "store_id": order.store_id,
            "status": order.status.value,
            "total_amount": order.total_amount,
            "shipping_address": order.shipping_address,
            "billing_address": order.billing_address,
            "payment_id": order.payment_id,
            "notes": order.notes,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "extra": order.extra
        }
        for order in orders
    ]