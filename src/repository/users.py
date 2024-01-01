from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.fu_db import get_db
from src.entity.models import User


async def update_token(user: User, token: str | None, db: AsyncSession):
    user.refresh_token = token
    await db.commit()


async def update_avatar_url(user: User, url: str | None, db: AsyncSession):
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user
