from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uuid, datetime
from sqlalchemy.orm import Session

from db import engine, SessionLocal, database
from models import Base, User, Machine, Transaction, UserCreate, DepositIn, TransactionOut
from auth import hash_password, verify_password, create_access_token, get_current_user

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Swachh ATM Prototype")

# Static and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Serve the single-page web UI
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Auth endpoints
@app.post("/api/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.phone == user.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Phone already registered")
    user_id = str(uuid.uuid4())
    db_user = User(id=user_id, name=user.name, phone=user.phone, hashed_password=hash_password(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    token = create_access_token({"sub": db_user.id, "name": db_user.name, "phone": db_user.phone})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/api/login")
def login(form: dict, db: Session = Depends(get_db)):
    phone = form.get("phone")
    password = form.get("password")
    user = db.query(User).filter(User.phone == phone).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.id, "name": user.name, "phone": user.phone})
    return {"access_token": token, "token_type": "bearer"}

# Simulate ATM registration for testing
@app.post("/api/machine/register")
def register_machine(data: dict, db: Session = Depends(get_db)):
    machine_id = data.get("id") or str(uuid.uuid4())
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        m = Machine(id=machine_id, location=data.get("location", "Unknown"), city=data.get("city", "Unknown"))
        db.add(m)
        db.commit()
        return {"id": machine_id}
    return {"id": machine_id}

# Deposit endpoint - called by frontend when user "scans" and deposits
@app.post("/api/deposit")
def deposit(deposit: DepositIn, credentials=Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = credentials.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Simple points calc
    points_per_kg = {
        "plastic": 10,
        "paper": 5,
        "metal": 15,
        "ewaste": 25,
        "other": 3,
    }
    pts = int(points_per_kg.get(deposit.waste_type.value, 1) * deposit.weight_kg)
    tx_id = str(uuid.uuid4())
    tx = Transaction(id=tx_id, user_id=user_id, machine_id=deposit.machine_id, waste_type=deposit.waste_type, weight_kg=deposit.weight_kg, points_earned=pts)
    user.points += pts
    db.add(tx)
    db.commit()
    return {"transaction_id": tx_id, "points_earned": pts, "new_total": user.points}

# Get transactions for a user
@app.get("/api/transactions")
def get_transactions(credentials=Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = credentials.get("sub")
    txs = db.query(Transaction).filter(Transaction.user_id == user_id).order_by(Transaction.timestamp.desc()).limit(100).all()
    return [TransactionOut.from_orm(t) for t in txs]

# Leaderboard (simple SQL aggregate)
@app.get("/api/leaderboard")
def leaderboard(db: Session = Depends(get_db)):
    # top 20 users by points
    users = db.query(User).order_by(User.points.desc()).limit(20).all()
    return [{"id": u.id, "name": u.name, "points": u.points} for u in users]