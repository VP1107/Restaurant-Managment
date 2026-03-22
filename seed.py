# seed.py
from database import session
from services import hash_password
import model

def create_owner(name: str, email: str, password: str):
    db = session()
    try:
        existing = db.query(model.User).filter(model.User.email == email).first()
        if existing:
            print(f"User {email} already exists with role: {existing.role}")
            return

        owner = model.User(
            name=name,
            email=email,
            password=hash_password(password),
            role="owner"
        )
        db.add(owner)
        db.commit()
        db.refresh(owner)
        print(f"Owner created: {owner.email} (id={owner.id})")
    finally:
        db.close()

if __name__ == "__main__":
    create_owner(
        name="Vatsal Pandya",
        email="vatsalpandya2007@gmail.com",
        password="vatsal123"
    )