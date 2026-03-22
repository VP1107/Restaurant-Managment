from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
db_url = os.getenv("DB_URL")
engine = create_engine(db_url)
session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
