from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from datetime import datetime
from app.models.order import StringingOrder
from pydantic import BaseModel
from typing import Optional
from app.models.order import StringingOrder, OrderStatus
import uuid
from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse


class StringingOrderCreate(BaseModel):
    sport: str
    racket_model: str
    string: str
    tension: str
    pickup_date: datetime 
    notes: Optional[str] = None  # Optional notes
    price: float

order_router = APIRouter()

@order_router.post("/order_stringing", status_code=201)
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

    headers = {"Location": f"/orders/{new_order.id}"}
    return JSONResponse(
        content={
            "message": "Stringing order created successfully",
            "order_id": new_order.id,
            "order_status": new_order.order_status.value
        },
        headers=headers,
        status_code=201
    )

@order_router.get("/orders/")
def get_orders(
    sport: Optional[str] = None,
    order_status: Optional[OrderStatus] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    GET method for retrieving a list of orders with optional filters for sport and status.
    """
    query = db.query(StringingOrder)
    
    if sport:
        query = query.filter(StringingOrder.sport == sport)
    
    if order_status:
        query = query.filter(StringingOrder.order_status == order_status)
    
    orders = query.offset(skip).limit(limit).all()
    return {"orders": orders}

@order_router.get("/orders/{order_id}")
def get_order(order_id: str, db: Session = Depends(get_db)):
    order = db.query(StringingOrder).filter(StringingOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {
        "order": order,
        "links": {
            "self": f"/orders/{order.id}",
            "update": f"/orders/{order.id}/status",
            "cancel": f"/orders/{order.id}/cancel"
        }
    }

class OrderUpdateStatus(BaseModel):
    order_status: OrderStatus

@order_router.put("/orders/{order_id}/status")
def update_order_status(order_id: str, update_status: OrderUpdateStatus, db: Session = Depends(get_db)):
    """
    PUT method to update an order's status (PENDING -> PAID -> STRUNG, etc.).
    """
    order = db.query(StringingOrder).filter(StringingOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.order_status = update_status.order_status
    order.updated_at = datetime.utcnow()  # Update the timestamp
    db.commit()
    db.refresh(order)
    
    return {"message": "Order status updated successfully", "order_status": order.order_status.value}


def update_order_background(order_id: str, db: Session):
    order = db.query(StringingOrder).filter(StringingOrder.id == order_id).first()
    if order:
        order.order_status = OrderStatus.STRUNG  # Update status as an example
        order.updated_at = datetime.utcnow()
        db.commit()
        
@order_router.post("/order_async_update", status_code=202)
def async_update_order(order_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    POST method to update an order asynchronously.
    """
    order = db.query(StringingOrder).filter(StringingOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Add task to background
    background_tasks.add_task(update_order_background, order_id, db)
    
    return {"message": "Order update in progress", "order_id": order_id}

@order_router.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )