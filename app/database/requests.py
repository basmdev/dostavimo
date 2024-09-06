from datetime import datetime
from typing import Optional

from sqlalchemy import select

from app.database.models import async_session
from app.database.models import User, Business, Courier, FastDelivery


# Добавление пользователя в базу
async def add_user(
    tg_id: int,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    username: Optional[str] = None,
    last_interaction: Optional[datetime] = None,
):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            user = User(
                tg_id=tg_id,
                first_name=first_name,
                last_name=last_name,
                username=username,
                last_interaction=last_interaction,
            )
            session.add(user)
            await session.commit()
        else:
            if first_name is not None:
                user.first_name = first_name
            if last_name is not None:
                user.last_name = last_name
            if username is not None:
                user.username = username
            if last_interaction is not None:
                user.last_interaction = last_interaction
            await session.commit()


# Добавление бизнеса в базу
async def add_business(
    business_name: str,
    address: str,
    contact_person: str,
    contact_phone: str,
    user_id: int,
):
    async with async_session() as session:
        new_business = Business(
            business_name=business_name,
            address=address,
            contact_person=contact_person,
            contact_phone=contact_phone,
            user_id=user_id,
        )

        session.add(new_business)

        user = await session.scalar(select(User).where(User.tg_id == user_id))
        if user:
            user.has_business = True
            await session.commit()

        await session.commit()


# Добавление курьера в базу
async def add_courier(
    courier_name: str, contact_phone: str, photo_url: str, user_id: int
):
    async with async_session() as session:
        new_courier = Courier(
            courier_name=courier_name,
            contact_phone=contact_phone,
            photo_url=photo_url,
            user_id=user_id,
        )

        session.add(new_courier)

        user = await session.scalar(select(User).where(User.tg_id == user_id))
        if user:
            user.is_courier = True
            await session.commit()

        await session.commit()


# Добавление быстрой доставки в базу
async def add_delivery(
    start_geo: str, end_geo: str, name: str, phone: str, comment: str
):
    async with async_session() as session:
        new_delivery = FastDelivery(
            start_geo=start_geo,
            end_geo=end_geo,
            name=name,
            phone=phone,
            comment=comment,
        )

        session.add(new_delivery)

        await session.commit()


# Обновление названия бизнеса
async def update_business_name(business_name: str, user_id: int):
    async with async_session() as session:
        business = await session.scalar(
            select(Business).where(Business.user_id == user_id)
        )

        if business:
            business.business_name = business_name
            await session.commit()
        else:
            raise ValueError("Бизнес для данного пользователя не найден.")


# Обновление адреса бизнеса
async def update_business_address(business_address: str, user_id: int):
    async with async_session() as session:
        business = await session.scalar(
            select(Business).where(Business.user_id == user_id)
        )

        if business:
            business.address = business_address
            await session.commit()
        else:
            raise ValueError("Бизнес для данного пользователя не найден.")


# Обновление контактного лица бизнеса
async def update_business_person(business_person: str, user_id: int):
    async with async_session() as session:
        business = await session.scalar(
            select(Business).where(Business.user_id == user_id)
        )

        if business:
            business.contact_person = business_person
            await session.commit()
        else:
            raise ValueError("Бизнес для данного пользователя не найден.")


# Обновление контактного телефона бизнеса
async def update_business_phone(business_phone: str, user_id: int):
    async with async_session() as session:
        business = await session.scalar(
            select(Business).where(Business.user_id == user_id)
        )

        if business:
            business.contact_phone = business_phone
            await session.commit()
        else:
            raise ValueError("Бизнес для данного пользователя не найден.")


# Получение информации о бизнесе
async def get_business_by_user_id(user_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Business).where(Business.user_id == user_id)
        )
        business = result.scalars().first()
        return business
