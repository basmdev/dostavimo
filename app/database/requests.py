from datetime import datetime
from typing import Optional

from sqlalchemy import delete, func, select, update

from app.database.models import Business, Courier, Delivery, User, async_session


# Получение информации о наличии бизнеса
async def get_user_has_business(user_id: int):
    async with async_session() as session:
        result = await session.execute(select(User).filter(User.tg_id == user_id))
        user = result.scalars().first()
        return user.has_business if user else False


# Получение координат бизнеса
async def get_business_coordinates(user_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Business).filter(Business.user_id == user_id)
        )
        business = result.scalars().first()
        return business.coordinates


# Получение информации о курьере
async def get_user_is_courier(user_id: int):
    async with async_session() as session:
        result = await session.execute(select(User).filter(User.tg_id == user_id))
        user = result.scalars().first()
        return user.is_courier if user else False


# Получение списка курьеров
async def get_couriers():
    async with async_session() as session:
        result = await session.execute(
            select(User.tg_id).filter(User.is_courier == True)
        )
        couriers = result.scalars().all()
        return couriers


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
    coordinates: str,
    contact_person: str,
    contact_phone: str,
    user_id: int,
):
    async with async_session() as session:
        new_business = Business(
            business_name=business_name,
            address=address,
            coordinates=coordinates,
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
    start_geo: str,
    end_geo: str,
    phone: str,
    price: int,
    yandex_url: str,
    client_phone: str,
    message_id: str,
    chat_id: str,
    business_id: int,
):
    async with async_session() as session:
        new_delivery = Delivery(
            start_geo=start_geo,
            end_geo=end_geo,
            phone=phone,
            price=price,
            yandex_url=yandex_url,
            client_phone=client_phone,
            message_id=message_id,
            chat_id=chat_id,
            business_id=business_id,
        )

        session.add(new_delivery)

        await session.commit()
        await session.refresh(new_delivery)
        return new_delivery.id


# Получение информации о бизнесе
async def get_business_by_user_id(user_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Business).where(Business.user_id == user_id)
        )
        business = result.scalars().first()
        return business


# Получение информации о курьере
async def get_courier_by_user_id(user_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Courier).where(Courier.user_id == user_id)
        )
        courier = result.scalars().first()
        return courier


# Обновление названия бизнеса
async def update_business_name(business_name: str, user_id: int):
    async with async_session() as session:
        business = await session.scalar(
            select(Business).where(Business.user_id == user_id)
        )

        business.business_name = business_name
        await session.commit()


# Обновление адреса бизнеса
async def update_business_address(
    business_address: str, coordinates: str, user_id: int
):
    async with async_session() as session:
        business = await session.scalar(
            select(Business).where(Business.user_id == user_id)
        )

        business.address = business_address
        business.coordinates = coordinates
        await session.commit()


# Обновление контактного лица бизнеса
async def update_business_person(business_person: str, user_id: int):
    async with async_session() as session:
        business = await session.scalar(
            select(Business).where(Business.user_id == user_id)
        )

        business.contact_person = business_person
        await session.commit()


# Обновление контактного телефона бизнеса
async def update_business_phone(business_phone: str, user_id: int):
    async with async_session() as session:
        business = await session.scalar(
            select(Business).where(Business.user_id == user_id)
        )

        business.contact_phone = business_phone
        await session.commit()


# Обновление контактного телефона курьера
async def update_courier_phone(courier_phone: str, user_id: int):
    async with async_session() as session:
        courier = await session.scalar(
            select(Courier).where(Courier.user_id == user_id)
        )

        courier.contact_phone = courier_phone
        await session.commit()


# Удаление профиля бизнеса из базы
async def delete_business_by_user_id(user_id: int):
    async with async_session() as session:
        await session.execute(delete(Business).where(Business.user_id == user_id))

        await session.execute(
            update(User).where(User.id == user_id).values(has_business=0)
        )

        await session.commit()


# Удаление профиля курьера из базы
async def delete_courier_by_user_id(user_id: int):
    async with async_session() as session:
        await session.execute(delete(Courier).where(Courier.user_id == user_id))

        await session.execute(
            update(User).where(User.id == user_id).values(is_courier=0)
        )

        await session.commit()


# Обновление статуса заказа
async def update_delivery_status(
    delivery_id: int, new_status: str, courier_id: int = None
):
    async with async_session() as session:
        statement = select(Delivery).where(Delivery.id == delivery_id)
        result = await session.execute(statement)
        delivery = result.scalars().first()
        delivery.status = new_status

        if courier_id:
            delivery.courier_id = courier_id

        await session.commit()
        await session.refresh(delivery)
        return delivery


# Сохранение чата и ID сообщения
async def save_chat_and_message_id(delivery_id: int, message_id: int, chat_id: int):
    async with async_session() as session:
        statement = select(Delivery).where(Delivery.id == delivery_id)
        result = await session.execute(statement)
        delivery = result.scalars().first()
        delivery.message_id = str(message_id)
        delivery.chat_id = str(chat_id)
        await session.commit()
        await session.refresh(delivery)


# Получение чата и ID сообщения
async def get_message_and_chat_id(delivery_id: int):
    async with async_session() as session:
        statement = select(Delivery.message_id, Delivery.chat_id).where(
            Delivery.id == delivery_id
        )
        result = await session.execute(statement)
        message_id, chat_id = result.fetchone()

        return message_id, chat_id


# Получение доставки по ID
async def get_delivery_by_id(delivery_id: int):
    async with async_session() as session:
        statement = select(Delivery).where(Delivery.id == delivery_id)

        result = await session.execute(statement)

        delivery = result.scalar_one_or_none()

        return delivery


# Получение списка заказов курьера
async def get_courier_deliveries(user_id: int, page: int, per_page: int):
    async with async_session() as session:
        offset = (page - 1) * per_page
        statement = (
            select(Delivery)
            .where(Delivery.courier_id == user_id)
            .order_by(Delivery.id.desc())
            .offset(offset)
            .limit(per_page)
        )
        result = await session.execute(statement)
        deliveries = result.scalars().all()

        return deliveries


# Получение списка заказов бизнеса
async def get_business_deliveries(user_id: int, page: int, per_page: int, status: str):
    async with async_session() as session:
        offset = (page - 1) * per_page
        statement = (
            select(Delivery)
            .where(Delivery.business_id == user_id, Delivery.status == status)
            .order_by(Delivery.id.desc())
            .offset(offset)
            .limit(per_page)
        )
        result = await session.execute(statement)
        deliveries = result.scalars().all()

        return deliveries


# Получение количества активных заказов
async def get_business_deliveries_count(user_id: int, status: str):
    async with async_session() as session:
        statement = select(func.count(Delivery.id)).where(
            Delivery.business_id == user_id, Delivery.status == status
        )
        result = await session.execute(statement)
        count = result.scalar()

        return count


# Получение деталей заказа по ID
async def get_order_details(order_id: int):
    async with async_session() as session:
        statement = select(Delivery).where(Delivery.id == order_id)
        result = await session.execute(statement)
        order = result.scalar_one_or_none()
        return order


# Изменение цены заказа
async def update_delivery_price(delivery_id: int, new_price: int):
    async with async_session() as session:
        delivery = await session.scalar(
            select(Delivery).where(Delivery.id == delivery_id)
        )
        delivery.price = new_price
        await session.commit()
