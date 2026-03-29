from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import restaurants, auth, dishes, booking, tables

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(restaurants.router)
app.include_router(auth.router)
app.include_router(dishes.router)
app.include_router(booking.router)
app.include_router(tables.router)