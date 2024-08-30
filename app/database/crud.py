from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import User, async_session


# Получение информации о наличии бизнеса
async def get_user_has_business(user_id: int, session: AsyncSession):
    async with async_session() as session:
        result = await session.execute(select(User).filter(User.tg_id == user_id))
        user = result.scalars().first()
        return user.has_business if user else False


# Получение информации о курьере
async def get_user_is_courier(user_id: int, session: AsyncSession):
    async with async_session() as session:
        result = await session.execute(select(User).filter(User.tg_id == user_id))
        user = result.scalars().first()
        return user.is_courier if user else False
