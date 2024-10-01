from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import engine, get_db
from app.models import order
from app.routers.order_service import order_router  # Import the order router
from fastapi.middleware.cors import CORSMiddleware

order.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(order_router, prefix="/orders", tags=["orders"])

@app.get("/")
def read_root():
    return {"Hello": "World"}
