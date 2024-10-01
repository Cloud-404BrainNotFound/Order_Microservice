from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from datetime import datetime
from app.models.order import StringingOrder
from pydantic import BaseModel
from typing import Optional
from app.models.order import StringingOrder, OrderStatus
import uuid


class StringingOrderCreate(BaseModel):
    sport: str
    racket_model: str
    string: str
    tension: str
    pickup_date: datetime 
    notes: Optional[str] = None  # Optional notes
    price: float

order_router = APIRouter()

@order_router.post("/order_stringing")
def create_stringing_order(
    order: StringingOrderCreate,
    db: Session = Depends(get_db),
):
    new_order = StringingOrder(
        sport=order.sport,
        racket_model=order.racket_model,
        string=order.string,
        tension=order.tension,
        pickup_date=order.pickup_date,
        notes=order.notes or "",  # Default to empty string if None
        price=order.price,
        order_status=OrderStatus.PENDING 
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return {
        "message": "Stringing order created successfully",
        "order_id": new_order.id,
        "order_status": new_order.order_status.value
    }