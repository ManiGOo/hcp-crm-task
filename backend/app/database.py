# backend/app/database.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()  # loads .env file

DATABASE_URL = os.getenv("DATABASE_URL")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,               # prints SQL queries in terminal → helpful for debugging
    future=True
)

# Session factory for async sessions
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for all our DB models (tables)
Base = declarative_base()

# Helper to get DB session in endpoints (we'll use later)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session