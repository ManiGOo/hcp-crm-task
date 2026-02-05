# backend/app/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, desc
from typing import List, Optional
from . import models, schemas  # we'll create schemas.py next

# backend/app/crud.py
async def create_interaction(db: AsyncSession, interaction: schemas.InteractionCreate) -> models.Interaction:
    # 1. Convert to dict (handles Pydantic v2 model_dump or v1 dict)
    data = interaction.model_dump() if hasattr(interaction, 'model_dump') else interaction.dict()
    
    # 2. FORCE values to strings (use the EXACT strings found in Step 1)
    # Example: if Step 1 returned 'MEETING', use data['interaction_type'] = 'MEETING'
    data['interaction_type'] = interaction.interaction_type.name
    if interaction.outcomes:
        data['outcomes'] = interaction.outcomes.name

    db_interaction = models.Interaction(**data)
    db.add(db_interaction)
    await db.commit()
    await db.refresh(db_interaction)
    return db_interaction

async def get_interactions(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Interaction]:
    """Get list of interactions (with pagination)."""
    result = await db.execute(select(models.Interaction).offset(skip).limit(limit))
    return result.scalars().all()
async def get_interaction(db: AsyncSession, interaction_id: int) -> Optional[models.Interaction]:
    """Get a single interaction by ID."""
    result = await db.execute(select(models.Interaction).filter(models.Interaction.id == interaction_id))
    return result.scalars().first()

async def get_most_recent_interaction(db: AsyncSession) -> Optional[models.Interaction]:
    """Get the most recent interaction from the database."""
    result = await db.execute(select(models.Interaction).order_by(desc(models.Interaction.id)).limit(1))
    return result.scalars().first()

async def get_interactions_by_hcp_name(db: AsyncSession, hcp_name: str) -> List[models.Interaction]:
    """Get interactions filtered by HCP name (case-insensitive search)."""
    result = await db.execute(
        select(models.Interaction).filter(
            models.Interaction.hcp_name.ilike(f"%{hcp_name}%")
        )
    )

    return result.scalars().all()

async def update_interaction(db: AsyncSession, interaction_id: int, updates: schemas.InteractionUpdate) -> Optional[models.Interaction]:
    """Update an existing interaction with new values."""
    stmt = (
        update(models.Interaction)
        .where(models.Interaction.id == interaction_id)
        .values(**updates.dict(exclude_unset=True))
        .returning(models.Interaction)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.scalars().first()

async def delete_interaction(db: AsyncSession, interaction_id: int) -> bool:
    """Delete an interaction (optional for demo)."""
    stmt = delete(models.Interaction).where(models.Interaction.id == interaction_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0