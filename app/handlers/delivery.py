from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.database.requests as rq
from app.database.models import async_session
from app.database.crud import get_couriers


router = Router()


class FastDelivery(StatesGroup):
    start_geo = State()
    end_geo = State()
    name = State()
    phone = State()
    comment = State()
    status = State()
    message_id = State()
    chat_id = State()


# Пункт меню "Срочная доставка"
@router.message(F.text == "Срочная доставка")
async def delivery_first(message: Message, state: FSMContext):
    await state.set_state(FastDelivery.start_geo)
    await message.answer("Укажите адрес, откуда забирать?")


@router.message(FastDelivery.start_geo)
async def delivery_second(message: Message, state: FSMContext):
    await state.update_data(start_geo=message.text)
    await state.set_state(FastDelivery.end_geo)
    await message.answer("Укажите адрес, куда доставить?")


@router.message(FastDelivery.end_geo)
async def delivery_third(message: Message, state: FSMContext):
    await state.update_data(end_geo=message.text)
    await state.set_state(FastDelivery.name)
    await message.answer("Имя получателя?")


@router.message(FastDelivery.name)
async def delivery_fourth(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(FastDelivery.phone)
    await message.answer("Номер телефона получателя?")


@router.message(FastDelivery.phone)
async def delivery_fourth(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.update_data(status="В ожидании")
    await state.set_state(FastDelivery.comment)
    await message.answer("Укажите комментарий к заказу")


@router.message(FastDelivery.comment)
async def delivery_fifth(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    data = await state.get_data()

    await message.answer(
        f"""Проверьте, все ли правильно?

<b>Начальный адрес:</b> {data['start_geo']}
<b>Адрес доставки:</b> {data['end_geo']}
<b>Имя получателя:</b> {data["name"]}
<b>Телефон получателя:</b> {data["phone"]}
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
        comment=data["comment"],
        message_id=data["message_id"],
        chat_id=data["chat_id"],
    )

    couriers = await get_couriers()
    for courier_id in couriers:
        try:
            await callback.bot.send_message(
                courier_id,
                f"""Заказ №{delivery_id}:

<b>Начальный адрес:</b> {data['start_geo']}
<b>Адрес доставки:</b> {data['end_geo']}
<b>Имя получателя:</b> {data["name"]}
<b>Телефон получателя:</b> {data["phone"]}
<b>Комментарий:</b> {data['comment']}

<b>Статус:</b> {data['status']}""",
                parse_mode="HTML",
                reply_markup=kb.get_delivery_action_keyboard(delivery_id),
            )

        except Exception as e:
            print(f"Не удалось отправить сообщение курьеру с ID {courier_id}: {e}")

    await callback.message.edit_text(
        f"""Заказ №{delivery_id}:

<b>Начальный адрес:</b> {data['start_geo']}
<b>Адрес доставки:</b> {data['end_geo']}
<b>Имя получателя:</b> {data["name"]}
<b>Телефон получателя:</b> {data["phone"]}
<b>Комментарий:</b> {data['comment']}

<b>Статус:</b> {data['status']}""",
        parse_mode="HTML",
    )
    await rq.save_chat_and_message_id(delivery_id, data["message_id"], data["chat_id"])
    await state.clear()


# Отмена срочной доставки
@router.callback_query(F.data == "delivery_no")
async def no_delivery(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Доставка отменена", reply_markup=kb.main)
    await state.clear()
