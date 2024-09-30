from sqlalchemy import create_engine, Column, String, Float, Integer, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import configparser
from datetime import datetime
import enum

config = configparser.ConfigParser()
config.read('config.ini')

DATABASE_URL = f"mysql://{config['database']['username']}:{config['database']['password']}@{config['database']['host']}:{config['database']['port']}/{config['database']['database']}"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
