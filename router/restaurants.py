from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from typing import List

import schema
import model
from services import get_db, get_role

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

# View all restaurants, view restaurant by id
@router.get("", response_model=List[schema.Restaurant])
def view_restaurants(db: Session = Depends(get_db)):
    db_restaurants = db.query(model.Restaurant).all()
    if db_restaurants:
        return db_restaurants
    return []

@router.get("/by-id/{id}", response_model=schema.Restaurant)
def view_restaurants_by_id(id: int, db: Session = Depends(get_db)):
    db_restaurant = db.query(model.Restaurant).filter(model.Restaurant.id == id).first()
    if db_restaurant:
        return db_restaurant
    raise HTTPException(status_code=404, detail="Restaurant not found")

@router.get("/by-name/{name}", response_model=schema.Restaurant)
def view_restaurants_by_name(name: str, db: Session = Depends(get_db)):
    db_restaurant = db.query(model.Restaurant).filter(model.Restaurant.name == name).first()
    if db_restaurant:
        return db_restaurant
    raise HTTPException(status_code=404, detail="Restaurant not found")

# Add restaurant
@router.post("", response_model=schema.Restaurant)
def add_restaurant(restaurant: schema.RestaurantCreate, db: Session = Depends(get_db), role: str = Depends(get_role)):
    if role != "owner":
        raise HTTPException(status_code=403, detail="Not authorized")
    db_restaurant = model.Restaurant(**restaurant.model_dump())
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant

# Update restaurant
@router.put("/{id}")
def update_restaurant(id: int, restaurant: schema.RestaurantCreate, db: Session = Depends(get_db), role: str = Depends(get_role)):
    if role != "owner":
        raise HTTPException(status_code=403, detail="Not authorized")
    db_restaurant = db.query(model.Restaurant).filter(model.Restaurant.id == id).first()
    if db_restaurant:
        update_data = restaurant.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_restaurant, key, value)
        db.commit()
        db.refresh(db_restaurant)
        return "Restaurant Updated"
    raise HTTPException(status_code=404, detail="Restaurant not found")

# Delete restaurant
@router.delete("/{id}")
def delete_restaurant(id: int, db: Session = Depends(get_db), role: str = Depends(get_role)):
    if role != "owner":
        raise HTTPException(status_code=403, detail="Not authorized")
    db_restaurant = db.query(model.Restaurant).filter(model.Restaurant.id == id).first()
    if db_restaurant:
        db.delete(db_restaurant)
        db.commit()
        return "Restaurant Deleted"
    raise HTTPException(status_code=404, detail="Restaurant not found")