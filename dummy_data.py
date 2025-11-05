from sqlalchemy.orm import Session
from models import User, Machine, Transaction, WasteType
import uuid, random, datetime
from auth import hash_password

def seed_dummy_data(db: Session):
    if db.query(User).count() > 0:
        return  # already seeded

    names = ["Vennela Vallabhaneni", "Riya Sharma", "Amit Patel", "Zoya Khan", "Aditya Verma", "Suresh Reddy", "Ananya Rao"]
    users = []
    for name in names:
        user = User(
            id=str(uuid.uuid4()),
            name=name,
            phone=f"+91{random.randint(7000000000,9999999999)}",
            hashed_password=hash_password("test123"),
            points=random.randint(100, 1200)
        )
        users.append(user)
        db.add(user)

    machines = []
    for city in ["Hyderabad", "Delhi", "Pune"]:
        for i in range(3):
            m = Machine(id=str(uuid.uuid4()), location=f"ATM-{city}-{i+1}", city=city)
            machines.append(m)
            db.add(m)

    db.commit()

    for user in users:
        for _ in range(random.randint(3, 10)):
            tx = Transaction(
                id=str(uuid.uuid4()),
                user_id=user.id,
                machine_id=random.choice(machines).id,
                waste_type=random.choice(list(WasteType)),
                weight_kg=round(random.uniform(0.3, 3.0), 2),
                points_earned=random.randint(5, 100),
                timestamp=datetime.datetime.utcnow() - datetime.timedelta(days=random.randint(0, 30))
            )
            db.add(tx)
    db.commit()
    print("✅ Dummy data seeded.")
