from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app import models
from app.database import engine, get_db
from app.models import order

from app.routers.order_service import order_router  # 导入订单相关的 router

# 创建数据库表

order.Base.metadata.create_all(bind=engine)


app = FastAPI()


# 这是一个router的示例

app.include_router(order_router, prefix="/orders", tags=["orders"])


@app.get("/")
def read_root():
    return {"Hello": "World"}