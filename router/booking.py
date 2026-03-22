from typing import List

from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from datetime import datetime

import schema
import model
from services import get_db, get_current_user

router = APIRouter(prefix="/booking", tags=["bookings"])

@router.post("/", response_model=schema.BookingResponse)
def create_booking(
    booking: schema.BookingCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Step 1: verify restaurant exists
    restaurant = db.query(model.Restaurant).filter(
        model.Restaurant.id == booking.restaurant_id
    ).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    # Step 2: find a table in this restaurant with enough capacity
    available_table = None
    tables = db.query(model.Table).filter(
        model.Table.restaurant_id == booking.restaurant_id,
        model.Table.capacity >= booking.guests,
        model.Table.booking_status == False     # not currently marked as booked
    ).all()

    # Step 3: from those tables, check none have a booking on the same date
    for table in tables:
        conflict = db.query(model.Booking).filter(
            model.Booking.table_id == table.id,
            model.Booking.date == booking.date,
            model.Booking.status == True        # only active bookings block the table
        ).first()
        if not conflict:
            available_table = table
            break

    if not available_table:
        raise HTTPException(
            status_code=400,
            detail="No available tables for the requested date and guest count"
        )

    # Step 4: create the booking using user_id from the JWT, not from the request
    db_booking = model.Booking(
        user_id=current_user["user_id"],
        restaurant_id=booking.restaurant_id,
        table_id=available_table.id,
        date=booking.date,
        guests=booking.guests,
        status=True
    )
    db.add(db_booking)

    # Step 5: mark the table as booked
    available_table.booking_status = True

    db.commit()
    db.refresh(db_booking)
    return db_booking

@router.delete("/{booking_id}")
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_booking = db.query(model.Booking).filter(
        model.Booking.id == booking_id
    ).first()
    if not db_booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Only the owner of the booking can cancel it
    if db_booking.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Free the table back up
    table = db.query(model.Table).filter(
        model.Table.id == db_booking.table_id
    ).first()
    
    other_active = db.query(model.Booking).filter(
    model.Booking.table_id == db_booking.table_id,
    model.Booking.status == True,
    model.Booking.id != booking_id
    ).first()
    if not other_active and table:
        table.booking_status = False

    db_booking.status = False   # mark booking as cancelled rather than deleting
    db.commit()
    db.refresh(db_booking)
    return {"message": "Booking cancelled successfully"}

@router.get("/my", response_model=List[schema.BookingResponse])
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    bookings = db.query(model.Booking).filter(
        model.Booking.user_id == current_user["user_id"]
    ).all()
    return bookings


@router.get("/admin/{restaurant_id}/bookings", response_model=List[schema.BookingResponse])
def get_bookings_for_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    restaurant = db.query(model.Restaurant).filter(
        model.Restaurant.id == restaurant_id
    ).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    if restaurant.admin_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    bookings = db.query(model.Booking).filter(
        model.Booking.restaurant_id == restaurant_id
    ).all()
    return bookings

# Additional admin endpoints for updating/cancelling any booking could be added similarly, with the same restaurant admin check.
@router.put("/{booking_id}/cancel")
def admin_cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_booking = db.query(model.Booking).filter(
        model.Booking.id == booking_id
    ).first()
    if not db_booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    restaurant = db.query(model.Restaurant).filter(
        model.Restaurant.id == db_booking.restaurant_id
    ).first()
    
    if restaurant.admin_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    table = db.query(model.Table).filter(
        model.Table.id == db_booking.table_id
    ).first()

    other_active = db.query(model.Booking).filter(
        model.Booking.table_id == db_booking.table_id,
        model.Booking.status == True,
        model.Booking.id != booking_id
    ).first()
    if not other_active and table:
        table.booking_status = False

    db_booking.status = False   # mark booking as cancelled rather than deleting
    db.commit()
    db.refresh(db_booking)
    return {"message": "Booking cancelled successfully by admin"}