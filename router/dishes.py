from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session

import schema
import model
from services import get_db, get_role

router = APIRouter(prefix="/dishes", tags=["dishes"])

# View all dishes, view dish by id, view dish by name
@router.get("")
def view_dishes(db: Session = Depends(get_db)):
    db_dishes = db.query(model.Dish).all()  # Fixed: schema.Dish -> model.Dish
    if db_dishes:
        return db_dishes
    return "No dishes found"

@router.get("/by-id/{id}")
def view_dishes_by_id(id: int, db: Session = Depends(get_db)):
    db_dishes = db.query(model.Dish).filter(model.Dish.id == id).first()
    if db_dishes:
        return db_dishes
    raise HTTPException(status_code=404, detail="Dish not found")

@router.get("/by-name/{name}", response_model=schema.DishResponse)
def view_dishes_by_name(name: str, db: Session = Depends(get_db)):
    db_dishes = db.query(model.Dish).filter(model.Dish.name == name).first()
    if db_dishes:
        return db_dishes
    raise HTTPException(status_code=404, detail="Dish not found")

# Add dish
@router.post("", response_model=schema.DishResponse)
def add_dish(dish: schema.DishCreate, db: Session = Depends(get_db), role: str = Depends(get_role)):
    if role != "owner":
        raise HTTPException(status_code=403, detail="Not authorized")
    db_dish = model.Dish(**dish.model_dump())
    if db.query(model.Dish).filter(model.Dish.name == db_dish.name).first():
        raise HTTPException(status_code=400, detail="Dish with this name already exists")
    db.add(db_dish)
    db.commit()
    db.refresh(db_dish)
    return db_dish

# Update dish
@router.put("/{id}")
def update_dish(id: int, dish: schema.DishUpdate, db: Session = Depends(get_db), role: str = Depends(get_role)):
    if role != "owner":
        raise HTTPException(status_code=403, detail="Not authorized")
    db_dish = db.query(model.Dish).filter(model.Dish.id == id).first()
    if db_dish:
        update_data = dish.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_dish, key, value)
        db.commit()
        db.refresh(db_dish)
        return "Dish Updated"
    raise HTTPException(status_code=404, detail="Dish not found")

# Delete dish
@router.delete("/{id}")
def delete_dish(id: int, db: Session = Depends(get_db), role: str = Depends(get_role)):
    if role != "owner":
        raise HTTPException(status_code=403, detail="Not authorized")
    db_dish = db.query(model.Dish).filter(model.Dish.id == id).first()
    if db_dish:
        db.delete(db_dish)
        db.commit()
        return "Dish Deleted"
    raise HTTPException(status_code=404, detail="Dish not found")