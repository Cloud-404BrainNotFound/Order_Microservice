from fastapi import FastAPI, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from app.database import engine, get_db
from app.models import order
from app.routers.order_service import order_router  # Import the order router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config.log import setup_logger
from app.dependecies.logging_middleware import logging_dependency

order.Base.metadata.create_all(bind=engine)
logger = setup_logger()

app = FastAPI()
app.middleware("http")(logging_dependency)

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

# Define the global exception handler for HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )