from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

import app.database.requests as rq
import app.keyboards as kb
from app.database.crud import get_couriers

router = Router()


class FastDelivery(StatesGroup):
    start_geo = State()
    end_geo = State()
    name = State()
    phone = State()
    comment = State()
    status = State()
    price = State()
    message_id = State()
    chat_id = State()


# Кнопка "Срочная доставка"
@router.message(F.text == "Срочная доставка")
async def delivery_first(message: Message, state: FSMContext):
    await state.set_state(FastDelivery.start_geo)
    await message.answer("Напишите адрес, откуда забирать?")


@router.message(FastDelivery.start_geo)
async def delivery_second(message: Message, state: FSMContext):
    await state.update_data(start_geo=message.text)
    await state.set_state(FastDelivery.end_geo)
    await message.answer("Напишите адрес, куда доставить?")


@router.message(FastDelivery.end_geo)
async def delivery_third(message: Message, state: FSMContext):
    await state.update_data(end_geo=message.text)
    await state.set_state(FastDelivery.name)
    await message.answer("Как зовут получателя?")


@router.message(FastDelivery.name)
async def delivery_fourth(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(FastDelivery.phone)
    await message.answer("Номер телефона получателя?")


@router.message(FastDelivery.phone)
async def delivery_fourth(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(FastDelivery.price)
    await message.answer("Сколько заплатите за доставку?")


@router.message(FastDelivery.price)
async def delivery_fifth(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(FastDelivery.comment)
    await message.answer("Нужно ли что-нибудь еще сообщить курьеру?")


@router.message(FastDelivery.comment)
async def delivery_sixth(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    await state.update_data(status="В ожидании")
    data = await state.get_data()

    await message.answer(
        f"""Проверьте, все ли правильно?

<b>Начальный адрес:</b> {data['start_geo']}
<b>Адрес доставки:</b> {data['end_geo']}
<b>Получатель:</b> {data["name"]}
<b>Телефон:</b> {data["phone"]}
<b>Цена за доставку:</b> {data["price"]}
<b>Комментарий:</b> {data['comment']}""",
        parse_mode="HTML",
        reply_markup=kb.fast_delivery,
    )


# Подтверждение срочной доставки
@router.callback_query(F.data == "delivery_yes")
async def confirm_delivery(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(message_id=callback.message.message_id)
    await state.update_data(chat_id=callback.message.chat.id)
    data = await state.get_data()

    delivery_id = await rq.add_delivery(
        start_geo=data["start_geo"],
        end_geo=data["end_geo"],
        name=data["name"],
        phone=data["phone"],
        price=data["price"],
        comment=data["comment"],
        message_id=data["message_id"],
        chat_id=data["chat_id"],
    )

    couriers = await get_couriers()
    for courier_id in couriers:
        await callback.bot.send_message(
            courier_id,
            f"""Заказ №{delivery_id}:

<b>Начальный адрес:</b> {data['start_geo']}
<b>Адрес доставки:</b> {data['end_geo']}

<b>Статус:</b> {data['status']}""",
            parse_mode="HTML",
            reply_markup=kb.get_more_keyboard(delivery_id),
        )

    await callback.message.edit_text(
        f"""Заказ №{delivery_id}:

<b>Начальный адрес:</b> {data['start_geo']}
<b>Адрес доставки:</b> {data['end_geo']}
<b>Получатель:</b> {data["name"]}
<b>Телефон:</b> {data["phone"]}
<b>Комментарий:</b> {data['comment']}

<b>Цена за доставку:</b> {data["price"]}
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
    await callback.message.answer("Доставка отменена", reply_markup=kb.main)
    await state.clear()


# Изменение цены заказа
@router.callback_query(F.data.startswith("adjust_price:"))
async def adjust_price(callback: CallbackQuery):
    await callback.answer()

    delivery_id, adjustment = map(int, callback.data.split(":")[1:])
    delivery = await rq.get_delivery_by_id(delivery_id)
    delivery.price += int(adjustment)

    await rq.update_delivery_price(delivery_id, delivery.price)

    await callback.message.edit_text(
        f"""Заказ №{delivery_id}:

<b>Начальный адрес:</b> {delivery.start_geo}
<b>Адрес доставки:</b> {delivery.end_geo}
<b>Получатель:</b> {delivery.name}
<b>Телефон:</b> {delivery.phone}
<b>Комментарий:</b> {delivery.comment}

<b>Цена за доставку:</b> {delivery.price}
<b>Статус:</b> {delivery.status}""",
        parse_mode="HTML",
        reply_markup=kb.get_price_adjustment_keyboard(delivery_id),
    )
