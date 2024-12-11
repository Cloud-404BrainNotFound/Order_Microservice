from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database import get_db
from datetime import datetime, timezone
from app.models.order import StringingOrder, OrderStatus, UserOrder
from pydantic import BaseModel, Field
from typing import Optional
from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse


# Pydantic model for order creation
class StringingOrderCreate(BaseModel):
    sport: str
    racket_model: str
    string: str
    tension: str
    pickup_date: Optional[datetime] = None
    notes: Optional[str] = Field(default="", max_length=1000)  # Limit notes to 1000 characters
    price: float

# Pydantic model for updating an order's info
class StringingOrderUpdate(BaseModel):
    sport: Optional[str] = None
    racket_model: Optional[str] = None
    string: Optional[str] = None
    tension: Optional[str] = None
    pickup_date: Optional[datetime] = None
    notes: Optional[str] = Field(default="", max_length=1000)
    price: Optional[float] = None


# Pydantic model for updating an order's status
class OrderUpdateStatus(BaseModel):
    order_status: OrderStatus

order_router = APIRouter()

# Create a new stringing order with error handling
@order_router.post("/order_stringing", status_code=201)
def create_stringing_order(
    order: StringingOrderCreate,
    db: Session = Depends(get_db),
):
    # Error list to collect validation issues
    errors = []
    
    # Validate sport
    valid_sports = ["Tennis", "Badminton", "Squash"]  # Example of valid sports
    if order.sport not in valid_sports:
        errors.append(f"Invalid sport: {order.sport}. Must be one of {valid_sports}.")

    # Validate tension
    try:
        tension = int(order.tension)
        if tension < 10 or tension > 70:
            errors.append("Tension must be between 10 and 70 lbs.")
    except ValueError:
        errors.append("Tension must be a valid number.")
    
    # Validate pickup date
    if order.pickup_date < datetime.now(timezone.utc):
        errors.append("Pickup date must be in the future.")

    # Validate price
    if order.price <= 0:
        errors.append("Price must be a positive value.")
    
    # If there are any validation errors, raise a 400 error
    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})

    try:
        # Create a new StringingOrder instance using validated Pydantic data
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
    
    except SQLAlchemyError as e:
        # Catch any database-related errors and return a 500 Internal Server Error
        db.rollback()  # Rollback the transaction in case of error
        raise HTTPException(status_code=500, detail="Database error occurred while creating the order.")

    except Exception as e:
        # Catch any unexpected errors
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

# Retrieve a list of orders with pagination and query parameters
@order_router.get("/orders/")
def get_orders(
    sport: Optional[str] = None,
    order_status: Optional[OrderStatus] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    query = db.query(StringingOrder)
    
    if sport:
        query = query.filter(StringingOrder.sport == sport)
    
    if order_status:
        query = query.filter(StringingOrder.order_status == order_status)
    
    orders = query.offset(skip).limit(limit).all()
    return {"orders": orders}

# Retrieve a single order by ID
@order_router.get("/orders/{order_id}")
def get_order(order_id: str, db: Session = Depends(get_db)):
    print(f"Looking for order with ID: {order_id}")  # Debugging print
    order = db.query(StringingOrder).filter(StringingOrder.id == order_id).first()
    if not order:
        print(f"Order not found for ID: {order_id}")  # Debugging print
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {
        "order": order,
        "links": {
            "self": f"/orders/{order.id}",
            "update": f"/orders/{order.id}/status",
            "cancel": f"/orders/{order.id}/cancel"
        }
    }

@order_router.put("/orders/{order_id}")
def update_order_info(order_id: str, order_update: StringingOrderUpdate, db: Session = Depends(get_db)):
    order = db.query(StringingOrder).filter(StringingOrder.id == order_id).first()
    
    # Check if the order exists
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Input validation errors
    errors = []
    
    # Validate sport (optional)
    if order_update.sport:
        valid_sports = ["Tennis", "Badminton", "Squash"]  # Example valid sports
        if order_update.sport not in valid_sports:
            errors.append(f"Invalid sport: {order_update.sport}. Must be one of {valid_sports}.")
    
    # Validate racket model (optional)
    if order_update.racket_model and len(order_update.racket_model) < 3:
        errors.append("Racket model name is too short.")
    
    # Validate string type (optional)
    if order_update.string and len(order_update.string) < 3:
        errors.append("String type is too short.")
    
    # Validate tension (optional)
    if order_update.tension:
        try:
            tension = int(order_update.tension)
            if tension < 10 or tension > 70:
                errors.append("Tension must be between 10 and 70 lbs.")
        except ValueError:
            errors.append("Tension must be a valid number.")
    
    # Validate pickup date (optional)
    if order_update.pickup_date and order_update.pickup_date < datetime.utcnow():
        errors.append("Pickup date must be in the future.")
    
    # Validate notes (optional)
    if order_update.notes and len(order_update.notes) > 1000:
        errors.append("Notes must not exceed 1000 characters.")
    
    # Validate price (optional)
    if order_update.price is not None and order_update.price <= 0:
        errors.append("Price must be a positive value.")
    
    # If any errors, raise a 400 Bad Request with the list of errors
    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    # Update only the fields that are provided and valid
    if order_update.sport:
        order.sport = order_update.sport
    if order_update.racket_model:
        order.racket_model = order_update.racket_model
    if order_update.string:
        order.string = order_update.string
    if order_update.tension:
        order.tension = order_update.tension
    if order_update.pickup_date:
        order.pickup_date = order_update.pickup_date
    if order_update.notes:
        order.notes = order_update.notes
    if order_update.price is not None:
        order.price = order_update.price
    
    order.updated_at = datetime.utcnow()  # Update the timestamp
    db.commit()
    db.refresh(order)
    
    return {"message": "Order info updated successfully", "order": order}


# Update order status
@order_router.put("/orders/{order_id}/status")
def update_order_status(order_id: str, update_status: OrderUpdateStatus, db: Session = Depends(get_db)):
    order = db.query(StringingOrder).filter(StringingOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.order_status = update_status.order_status
    order.updated_at = datetime.utcnow()  # Update the timestamp
    db.commit()
    db.refresh(order)
    
    return {"message": "Order status updated successfully", "order_status": order.order_status.value}

# Asynchronous order status update
def update_order_background(order_id: str, db: Session):
    order = db.query(StringingOrder).filter(StringingOrder.id == order_id).first()
    if order:
        order.order_status = OrderStatus.STRUNG  # Update status as an example
        order.updated_at = datetime.utcnow()
        db.commit()

@order_router.post("/order_async_update/{order_id}", status_code=202)
def async_update_order(order_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    order = db.query(StringingOrder).filter(StringingOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Add task to background
    background_tasks.add_task(update_order_background, order_id, db)
    
    return {"message": "Order update in progress", "order_id": order_id}

# Delete an order by ID
@order_router.delete("/orders/{order_id}", status_code=204)
def delete_order(order_id: str, db: Session = Depends(get_db)):
    order = db.query(StringingOrder).filter(StringingOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db.delete(order)
    db.commit()
    return {"message": "Order deleted successfully"}

@order_router.get("/orders/user/{user_id}")
def get_user_orders(
    user_id: str,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    # Get order IDs for the user
    user_orders = db.query(UserOrder).filter(UserOrder.user_id == user_id).all()
    order_ids = [uo.order_id for uo in user_orders]
    
    # Get the actual orders
    orders = (
        db.query(StringingOrder)
        .filter(StringingOrder.id.in_(order_ids))
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return {
        "orders": orders,
        "total": len(orders)
    }

@order_router.post("/order_stringing/user/{user_id}", status_code=201)
def create_user_stringing_order(
    user_id: str,
    order: StringingOrderCreate,
    db: Session = Depends(get_db),
):
    try:
        # Create new stringing order
        new_order = StringingOrder(
            sport=order.sport,
            racket_model=order.racket_model,
            string=order.string,
            tension=order.tension,
            pickup_date=order.pickup_date,
            notes=order.notes or "",
            price=order.price,
            order_status=OrderStatus.STRUNG
        )
        
        db.add(new_order)
        db.flush()  # Flush to get the new_order.id
        
        # Create user-order relationship
        user_order = UserOrder(
            user_id=user_id,
            order_id=new_order.id
        )
        
        db.add(user_order)
        db.commit()
        db.refresh(new_order)
        
        headers = {"Location": f"/orders/{new_order.id}"}
        return JSONResponse(
            content={
                "message": "Stringing order created successfully",
                "order_id": new_order.id,
                "user_id": user_id,
                "order_status": new_order.order_status.value
            },
            headers=headers,
            status_code=201
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while creating the order.")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
