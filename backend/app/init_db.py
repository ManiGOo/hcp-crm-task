import asyncio
import sys
import os
import sqlalchemy as sa

# Ensure the app directory is in path if running from backend folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base
from app import models  # Essential: Base needs to see the models

async def init_db():
    async with engine.begin() as conn:
        print("Dropping existing tables and enums...")
        # drop_all deletes tables, but sometimes you need to manually
        # drop types if SQLAlchemy doesn't track them perfectly
        await conn.execute(sa.text("DROP TYPE IF EXISTS outcometype CASCADE"))
        await conn.execute(sa.text("DROP TYPE IF EXISTS interactiontype CASCADE"))

        await conn.run_sync(Base.metadata.drop_all)

        print("Creating new tables and enum types...")
        await conn.run_sync(Base.metadata.create_all)

    print("🚀 Database reset successfully! Enums are now synced.")

if __name__ == "__main__":
    asyncio.run(init_db())

