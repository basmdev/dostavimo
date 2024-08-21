from datetime import datetime
from typing import Optional

from sqlalchemy import select

from app.database.models import async_session
from app.database.models import User

async def add_user(
    tg_id: int,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    username: Optional[str] = None,
    last_interaction: Optional[datetime] = None
):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            user = User(
                tg_id=tg_id,
                first_name=first_name,
                last_name=last_name,
                username=username,
                last_interaction=last_interaction
            )
            session.add(user)
            await session.commit()
        else:
            user.first_name = first_name or user.first_name
            user.last_name = last_name or user.last_name
            user.username = username or user.username
            user.last_interaction = last_interaction or user.last_interaction
            await session.commit()