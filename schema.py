from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime

class Dish(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None

class DishResponse(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None
    class Config:
        from_attributes = True

class DishUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    
class DishCreate(BaseModel):
    name: str
    price: float
    description: Optional[str] = None

class User(BaseModel):
    id: int
    name: str
    email: str
    role: Optional[Literal["admin", "owner", "customer"]] = "customer"

    class Config:
        from_attributes = True

class UserCredentials(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    name: str
    email: str
    password: str

class PromoteUser(BaseModel):
    id: int

class Restaurant(BaseModel):
    id: int
    name: str
    location: str
    admin_id: int
    table_count: Optional[int] = 4
    class Config:
        from_attributes = True
    
class RestaurantCreate(BaseModel):
    name: str
    location: str
    admin_id: int
    table_count: Optional[int] = 4

class Table(BaseModel):
    id: int
    restaurant_id: int
    number: int
    capacity: int
    booking_status: bool
    class Config:
        from_attributes = True

class TableCreate(BaseModel):
    restaurant_id: int
    number: int
    capacity: int
    booking_status: Optional[bool] = False

class Booking(BaseModel):
    id: int
    user_id: int
    restaurant_id: int
    table_id: int
    date: datetime
    guests: int
    status: bool
    class Config:
        from_attributes = True

class BookingCreate(BaseModel):
    restaurant_id: int
    date: datetime
    guests: int
    
class BookingResponse(BaseModel):
    id: int
    user_id: int
    restaurant_id: int
    table_id: int
    date: datetime
    guests: int
    status: bool
    class Config:
        from_attributes = True