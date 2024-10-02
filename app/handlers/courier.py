from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

import app.database.requests as rq
import app.keyboards as kb

COURIER_PAGES = 7

router = Router()


class CourierReg(StatesGroup):
    courier_name = State()
    contact_phone = State()
    photo_url = State()


class EditCourier(StatesGroup):
    edit_name = State()
    edit_contact_phone = State()


# Пункт меню "Я курьер"
@router.message(F.text == "Я курьер")
async def courier(message: Message):
    await message.answer("Желаете пройти регистрацию?", reply_markup=kb.courier)


# Кнопка отмены регистрации курьера
@router.callback_query(F.data == "courier_no")
async def business_reg_first(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()


# Кнопка регистрации курьера
@router.callback_query(F.data == "courier_yes")
async def courier_reg_first(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    await state.update_data(user_id=user_id)
    await state.set_state(CourierReg.courier_name)
    await callback.message.answer("Как Вас зовут?")


@router.message(CourierReg.courier_name)
async def courier_reg_second(message: Message, state: FSMContext):
    await state.update_data(courier_name=message.text)
    await state.set_state(CourierReg.contact_phone)
    await message.answer("Ваш номер телефона?")


@router.message(CourierReg.contact_phone)
async def courier_reg_third(message: Message, state: FSMContext):
    await state.update_data(contact_phone=message.text)
    await state.set_state(CourierReg.photo_url)
    await message.answer("Отправьте фото своего паспорта")


@router.message(CourierReg.photo_url)
async def courier_reg_fourth(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("Пожалуйста, отправьте фото паспорта")
        return

    photo_id = message.photo[-1].file_id

    photo = await message.bot.get_file(photo_id)

    user_id = message.from_user.id

    file_name = f"photos/{user_id}.jpg"

    await message.bot.download_file(photo.file_path, file_name)

    await state.update_data(photo_url=file_name)

    data = await state.get_data()
    await message.answer(
        f"""Проверьте, все ли правильно:
<b>Имя:</b> {data["courier_name"]}
<b>Телефон:</b> {data["contact_phone"]}""",
        parse_mode="HTML",
        reply_markup=kb.reg_done_courier,
    )


# Подтверждение регистрации курьера
@router.callback_query(F.data == "reg_yes_courier")
async def confirm_reg(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    await rq.add_courier(
        courier_name=data["courier_name"],
        contact_phone=data["contact_phone"],
        photo_url=data["photo_url"],
        user_id=data["user_id"],
    )
    await callback.message.answer(
        "Регистрация прошла успешно", reply_markup=kb.main_courier
    )
    await state.clear()


# Отмена регистрации курьера
@router.callback_query(F.data == "reg_no_courier")
async def no_reg(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        "Регистрация отменена, хотите начать заново?", reply_markup=kb.courier
    )
    await state.clear()


# Личный кабинет курьера
@router.message(F.text == "Личный кабинет курьера")
async def cabinet_courier(message: Message):
    await message.answer("Личный кабинет курьера", reply_markup=kb.courier_profile)


# Изменение профиля курьера
@router.callback_query(F.data == "edit_profile_courier")
async def edit_profile_courier(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id

    courier = await rq.get_courier_by_user_id(user_id)

    name = courier.courier_name
    phone = courier.contact_phone
    await callback.message.edit_text(
        f"""<b>Имя:</b> {name}
<b>Контактный телефон:</b> {phone}""",
        reply_markup=kb.courier_edit_profile,
        parse_mode="HTML",
    )


# Переход назад в профиле курьера
@router.callback_query(F.data == "courier_back")
async def courier_back(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "Личный кабинет курьера", reply_markup=kb.courier_profile
    )


# Изменение контактного телефона
@router.callback_query(F.data == "courier_change_phone")
async def change_courier_phone(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(EditCourier.edit_contact_phone)
    await callback.message.answer("Введите новый номер телефона")


@router.message(EditCourier.edit_contact_phone)
async def update_courier_phone(message: Message, state: FSMContext):
    new_phone = message.text
    user_id = message.from_user.id

    await rq.update_courier_phone(
        courier_phone=new_phone,
        user_id=user_id,
    )

    await message.answer(
        f"<b>Новый номер:</b> {new_phone}",
        reply_markup=kb.main_courier,
        parse_mode="HTML",
    )
    await state.clear()


# Удаление профиля курьера
@router.callback_query(F.data == "delete_profile_courier")
async def delete_courier_profile(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        "Вы уверены, что хотите удалить свой профиль?",
        reply_markup=kb.confirm_delete_courier,
    )


# Подтверждение удаления курьера
@router.callback_query(F.data == "confirm_delete_courier")
async def delete_courier(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id

    await rq.delete_courier_by_user_id(user_id)

    await callback.message.answer("Профиль удален", reply_markup=kb.main)


# Отмена удаления бизнеса
@router.callback_query(F.data == "cancel_delete_courier")
async def cancel_delete_courier(callback: CallbackQuery):
    await callback.answer()

    await callback.message.answer(
        "Удаление профиля отменено", reply_markup=kb.main_courier
    )


# Принятие заказа на доставку
@router.callback_query(F.data.startswith("accept_delivery_"))
async def accept_delivery(callback: CallbackQuery):
    await callback.answer()

    delivery_id = int(callback.data.split("_")[2])
    delivery = await rq.get_delivery_by_id(delivery_id)

    if delivery.status != "В ожидании":
        await callback.message.answer(f"Заказ №{delivery.id} принят другим курьером")
        return

    courier_id = callback.from_user.id
    delivery = await rq.update_delivery_status(
        delivery_id, "Принято курьером", courier_id=courier_id
    )
    courier = await rq.get_courier_by_user_id(courier_id)

    if delivery:
        await callback.message.edit_text(
            f"""Заказ №{delivery.id}:

<b>Начальный адрес:</b> {delivery.start_geo}
<b>Адрес доставки:</b> {delivery.end_geo}
<b>Имя получателя:</b> {delivery.name}
<b>Телефон получателя:</b> {delivery.phone}
<b>Комментарий:</b> {delivery.comment}

<b>Статус:</b> {delivery.status}""",
            parse_mode="HTML",
        )
    else:
        await callback.message.answer("Статус заказа не обновлен")

    try:
        message_id, chat_id = await rq.get_message_and_chat_id(delivery_id)
        if message_id and chat_id:
            await callback.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=(
                    f"""Заказ №{delivery.id}:

<b>Начальный адрес:</b> {delivery.start_geo}
<b>Адрес доставки:</b> {delivery.end_geo}
<b>Имя получателя:</b> {delivery.name}
<b>Телефон получателя:</b> {delivery.phone}
<b>Комментарий:</b> {delivery.comment}

<b>Статус:</b> {delivery.status}"""
                ),
                parse_mode="HTML",
            )
            await callback.message.answer(
                f"""Заказ №{delivery.id}:

<b>Ваш курьер:</b> {courier.courier_name}
<b>Телефон курьера:</b> {courier.contact_phone}""",
                parse_mode="HTML",
            )
        else:
            return None

    except Exception as e:
        raise Exception(f"Не удалось отредактировать сообщение: {e}")


# Отмена заказа на доставку
@router.callback_query(F.data.startswith("decline_delivery_"))
async def decline_delivery(callback: CallbackQuery):
    await callback.answer()
    delivery_id = int(callback.data.split("_")[2])
    delivery = await rq.get_delivery_by_id(delivery_id)
    await callback.message.edit_text(f"Заказ №{delivery.id} отменен")


# Принятые заказы
@router.callback_query(F.data.startswith("courier_deliveries"))
async def courier_deliveries(callback: CallbackQuery):
    await callback.answer()

    user_id = callback.from_user.id
    page = int(callback.data.split(":")[1]) if ":" in callback.data else 1
    per_page = COURIER_PAGES

    deliveries = await rq.get_courier_deliveries(user_id, page, per_page)

    if not deliveries:
        await callback.message.answer("История заказов пуста")
        return

    keyboard_builder = kb.InlineKeyboardBuilder()

    for delivery in deliveries:
        button_text = f"Заказ №{delivery.id}"
        button_callback_data = f"order_detail:{delivery.id}"
        keyboard_builder.button(text=button_text, callback_data=button_callback_data)

    if page > 1:
        keyboard_builder.button(
            text="Назад", callback_data=f"courier_deliveries:{page - 1}"
        )

    if len(deliveries) == per_page:
        next_deliveries = await rq.get_courier_deliveries(user_id, page + 1, per_page)
        if next_deliveries:
            keyboard_builder.button(
                text="Вперед", callback_data=f"courier_deliveries:{page + 1}"
            )

    keyboard_builder.adjust(2)

    keyboard = keyboard_builder.as_markup()

    if callback.message:
        await callback.message.edit_text(
            "История принятых заказов", reply_markup=keyboard
        )


# Детали принятого заказа
@router.callback_query(F.data.startswith("order_detail:"))
async def order_detail(callback: CallbackQuery):
    await callback.answer()
    order_id = int(callback.data.split(":")[1])

    order_details = await rq.get_order_details(order_id)

    details_text = f"""<b>Заказ №{order_id}:</b>

<b>Начальный адрес:</b> {order_details.start_geo}
<b>Адрес доставки:</b> {order_details.end_geo}
<b>Имя получателя:</b> {order_details.name}
<b>Телефон получателя:</b> {order_details.phone}
<b>Комментарий:</b> {order_details.comment}"""

    await callback.message.answer(details_text, parse_mode="HTML")
