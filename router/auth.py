from fastapi import  APIRouter ,HTTPException, Depends
from sqlalchemy.orm import Session

import schema
import model
from services import get_db, create_access_token, hash_password, verify_password, get_role

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(user: schema.UserRegister, db:Session=Depends(get_db)):
    if db.query(model.User).filter(model.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hash_password(user.password)
    db_user = model.User(name=user.name, email=user.email, password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "User registered successfully"}

@router.post("/login")
def login(user: schema.UserCredentials, db:Session=Depends(get_db)):
    db_user = db.query(model.User).filter(model.User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    access_token = create_access_token(data={"sub": str(db_user.id), "role": db_user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/promotion")
def create_promotion(promotion: schema.PromoteUser, db:Session=Depends(get_db), role:str = Depends(get_role)):
    if role != "owner":
        raise HTTPException(status_code=403, detail="Not authorized")
    db_user = db.query(model.User).filter(model.User.id == promotion.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.role = "admin"
    db.commit()
    db.refresh(db_user)
    return {"message": "User promoted to admin successfully"}
    