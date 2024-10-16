from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

import app.database.requests as rq
import app.keyboards as kb
from app.utils import get_coordinates, get_coordinates_for_one_address

router = Router()


class Delivery(StatesGroup):
    start_geo = State()
    end_geo = State()
    phone = State()
    client_phone = State()
    status = State()
    price = State()
    yandex_url = State()
    message_id = State()
    chat_id = State()


# Кнопка "Срочная доставка"
@router.message(F.text == "Срочная доставка")
async def delivery_first(message: Message, state: FSMContext):
    await state.set_state(Delivery.start_geo)
    await message.answer("Напишите адрес, откуда забирать?")


@router.message(Delivery.start_geo)
async def delivery_second(message: Message, state: FSMContext):
    await state.update_data(start_geo=message.text)
    await state.set_state(Delivery.end_geo)
    await message.answer("Напишите адрес, куда доставить?")


@router.message(Delivery.end_geo)
async def delivery_third(message: Message, state: FSMContext):
    await state.update_data(end_geo=message.text)
    await state.set_state(Delivery.client_phone)
    await message.answer("Ваш номер для связи?")


@router.message(Delivery.client_phone)
async def delivery_fourth(message: Message, state: FSMContext):
    await state.update_data(client_phone=message.text)
    await state.set_state(Delivery.phone)
    await message.answer("Номер получателя для связи?")


@router.message(Delivery.phone)
async def delivery_fifth(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(Delivery.price)
    await message.answer("Сколько заплатите за доставку?")


@router.message(Delivery.price)
async def delivery_sixth(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.update_data(status="В ожидании")
    data = await state.get_data()

    await message.answer(
        f"""Проверьте, все ли правильно?

<b>Откуда:</b> {data['start_geo']}
<b>Куда:</b> {data['end_geo']}
<b>Получатель:</b> {data["phone"]}
<b>Заказчик:</b> {data["client_phone"]}
<b>Цена:</b> {data["price"]} рублей""",
        parse_mode="HTML",
        reply_markup=kb.fast_delivery,
    )


# Подтверждение срочной доставки
@router.callback_query(F.data == "delivery_yes")
async def confirm_delivery(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user = callback.from_user
    has_business = await rq.get_user_has_business(user.id)
    await state.update_data(message_id=callback.message.message_id)
    await state.update_data(chat_id=callback.message.chat.id)
    await state.update_data(business_id=callback.message.chat.id)
    data = await state.get_data()

    end_coordinates = get_coordinates_for_one_address(data["end_geo"])

    if has_business:
        start_coordinates = await rq.get_business_coordinates(user.id)
        yandex_url = f"https://yandex.ru/maps/?rtext={start_coordinates}~{end_coordinates}&rtt=auto"
    else:
        yandex_url = get_coordinates(data["start_geo"], data["end_geo"])

    await state.update_data(yandex_url=yandex_url)
    data = await state.get_data()

    delivery_id = await rq.add_delivery(
        start_geo=data["start_geo"],
        end_geo=data["end_geo"],
        phone=data["phone"],
        price=data["price"],
        yandex_url=data["yandex_url"],
        client_phone=data["client_phone"],
        message_id=data["message_id"],
        chat_id=data["chat_id"],
        business_id=data["business_id"],
    )

    couriers = await rq.get_couriers()
    for courier_id in couriers:
        await callback.bot.send_message(
            courier_id,
            text=f"""Новый заказ №{delivery_id}:

<b>Откуда:</b> {data['start_geo']}
<b>Куда:</b> {data['end_geo']}""",
            parse_mode="HTML",
            reply_markup=kb.get_more_keyboard(delivery_id),
        )

    await callback.message.edit_text(
        f"""Заказ №{delivery_id}:

<b>Откуда:</b> {data['start_geo']}
<b>Куда:</b> {data['end_geo']}
<b>Получатель:</b> {data["phone"]}
<b>Заказчик:</b> {data['client_phone']}

<b>Цена:</b> {data["price"]} рублей
<b>Статус:</b> {data['status']}""",
        parse_mode="HTML",
        reply_markup=kb.get_price_adjustment_keyboard(delivery_id),
    )
    await rq.save_chat_and_message_id(delivery_id, data["message_id"], data["chat_id"])
    await state.clear()


# Отмена срочной доставки
@router.callback_query(F.data == "delivery_no")
async def no_delivery(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text("Создание заказа отменено")
    await state.clear()


# Изменение цены заказа
@router.callback_query(F.data.startswith("adjust_price:"))
async def adjust_price(callback: CallbackQuery):
    await callback.answer()

    delivery_id, adjustment = map(int, callback.data.split(":")[1:])
    delivery = await rq.get_delivery_by_id(delivery_id)
    delivery.price += int(adjustment)

    if delivery.price < 0:
        delivery.price = 0

    await rq.update_delivery_price(delivery_id, delivery.price)

    await callback.message.edit_text(
        f"""Заказ №{delivery_id}:

<b>Откуда:</b> {delivery.start_geo}
<b>Куда:</b> {delivery.end_geo}
<b>Получатель:</b> {delivery.phone}
<b>Заказчик:</b> {delivery.client_phone}

<b>Цена:</b> {delivery.price} рублей
<b>Статус:</b> {delivery.status}""",
        parse_mode="HTML",
        reply_markup=kb.get_price_adjustment_keyboard(delivery_id),
    )


# Отмена заказа
@router.callback_query(F.data.startswith("cancel_delivery:"))
async def cancel_delivery(callback: CallbackQuery):
    await callback.answer()

    delivery_id = int(callback.data.split(":")[-1])
    delivery = await rq.get_delivery_by_id(delivery_id)

    await rq.update_delivery_status(delivery_id, "Отменен")
    await callback.message.edit_text(
        f"""Заказ №{delivery_id}:

<b>Откуда:</b> {delivery.start_geo}
<b>Куда:</b> {delivery.end_geo}
<b>Получатель:</b> {delivery.phone}
<b>Заказчик:</b> {delivery.client_phone}

<b>Цена:</b> {delivery.price} рублей
<b>Статус:</b> Отменен""",
        parse_mode="HTML",
    )
