# db.py - simple databases wrapper using SQLAlchemy & databases
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from databases import Database

DATABASE_URL = "sqlite:///./swachh_atm.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()

database = Database(DATABASE_URL)