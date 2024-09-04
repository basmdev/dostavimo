from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.database.requests as rq
from app.database.crud import get_couriers


router = Router()


class FastDelivery(StatesGroup):
    start_geo = State()
    end_geo = State()
    name = State()
    phone = State()
    comment = State()


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
<b>Номер телефона получателя:</b> {data["phone"]}
<b>Комментарий:</b> {data['comment']}""",
        parse_mode="HTML",
        reply_markup=kb.fast_delivery,
    )


# Подтверждение срочной доставки
@router.callback_query(F.data == "delivery_yes")
async def confirm_delivery(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()

    await rq.add_delivery(
        start_geo=data["start_geo"],
        end_geo=data["end_geo"],
        name=data["name"],
        phone=data["phone"],
        comment=data["comment"],
    )

    couriers = await get_couriers()
    for courier_id in couriers:
        try:
            await callback.bot.send_message(
                courier_id,
                f"""Новый заказ на доставку:
<b>Начальный адрес:</b> {data['start_geo']}
<b>Адрес доставки:</b> {data['end_geo']}
<b>Имя получателя:</b> {data["name"]}
<b>Номер телефона получателя:</b> {data["phone"]}
<b>Комментарий:</b> {data['comment']}""",
                parse_mode="HTML",
                reply_markup=kb.delivery_action,
            )
        except Exception as e:
            print(f"Не удалось отправить сообщение курьеру с ID {courier_id}: {e}")

    await callback.message.answer(
        "Информация отправлена курьерам, ждите", reply_markup=kb.main
    )
    await state.clear()


# Отмена срочной доставки
@router.callback_query(F.data == "delivery_no")
async def no_delivery(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Доставка отменена", reply_markup=kb.main)
    await state.clear()
