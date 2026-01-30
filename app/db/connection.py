from app.config import DATABASE_URL
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
