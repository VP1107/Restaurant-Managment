from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from database import engine

Base = declarative_base()

class Dish(Base):
    __tablename__ = "dishes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    description = Column(String, nullable=True)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    restaurants = relationship("Restaurant", back_populates="admin")
    bookings = relationship("Booking", back_populates="user")


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    location = Column(String, nullable=False, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    table_count = Column(Integer, nullable=True)
    guest_count = Column(Integer, nullable=True)
    tables = relationship("Table", back_populates="restaurant")
    admin = relationship("User", back_populates="restaurants")
    bookings = relationship("Booking", back_populates="restaurant")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    guests = Column(Integer, nullable=False)
    status = Column(Boolean, nullable=False)
    table = relationship("Table", back_populates="bookings")
    user = relationship("User", back_populates="bookings")
    restaurant = relationship("Restaurant", back_populates="bookings")

class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    number = Column(Integer, nullable=False)
    capacity = Column(Integer, nullable=False)
    booking_status = Column(Boolean, nullable=False)
    restaurant = relationship("Restaurant", back_populates="tables")
    bookings = relationship("Booking", back_populates="table")

Base.metadata.create_all(bind=engine)
