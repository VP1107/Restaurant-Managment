from fastapi import FastAPI, Depends, HTTPException
from database import session, engine
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import router
from router import restaurants, auth, dishes, booking, tables
import schema
import model

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(restaurants.router)
app.include_router(auth.router)
app.include_router(dishes.router)
app.include_router(booking.router)
app.include_router(tables.router)
