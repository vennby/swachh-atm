import datetime
import enum
from sqlalchemy import Table, Column, String, Integer, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from pydantic import BaseModel, ConfigDict

Base = declarative_base()

class WasteType(str, enum.Enum):
    plastic = "plastic"
    paper = "paper"
    metal = "metal"
    ewaste = "ewaste"
    other = "other"

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    points = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Machine(Base):
    __tablename__ = "machines"
    id = Column(String, primary_key=True, index=True)
    location = Column(String)
    city = Column(String)
    status = Column(String, default="active")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    machine_id = Column(String, ForeignKey("machines.id"))
    waste_type = Column(Enum(WasteType))
    weight_kg = Column(Float)
    points_earned = Column(Integer)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

# Pydantic schemas
class UserCreate(BaseModel):
    name: str
    phone: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class DepositIn(BaseModel):
    machine_id: str
    waste_type: WasteType
    weight_kg: float

class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)