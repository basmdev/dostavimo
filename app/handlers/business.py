from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

import app.database.requests as rq
import app.keyboards as kb
from config import ORDER_PAGES

router = Router()


class BusinessReg(StatesGroup):
    business_name = State()
    address = State()
    contact_person = State()
    contact_phone = State()


class EditBusiness(StatesGroup):
    edit_name = State()
    edit_address = State()
    edit_contact_person = State()
    edit_contact_phone = State()


class BusinessDelivery(StatesGroup):
    start_geo = State()
    end_geo = State()
    phone = State()
    client_phone = State()
    status = State()
    price = State()
    message_id = State()
    chat_id = State()


# Кнопка "Я предприниматель"
@router.message(F.text == "Я предприниматель")
async def business(message: Message):
    await message.answer("Желаете пройти регистрацию?", reply_markup=kb.business)


# Кнопка отмены регистрации бизнеса
@router.callback_query(F.data == "business_no")
async def business_reg_first(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text("Регистрация бизнеса отменена")


# Кнопка регистрации бизнеса
@router.callback_query(F.data == "business_yes")
async def business_reg_first(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    await state.update_data(user_id=user_id)
    await state.set_state(BusinessReg.business_name)
    await callback.message.edit_reply_markup()
    await callback.message.answer("Как называется Ваш бизнес?")


@router.message(BusinessReg.business_name)
async def business_reg_second(message: Message, state: FSMContext):
    await state.update_data(business_name=message.text)
    await state.set_state(BusinessReg.address)
    await message.answer("Какой у Вашего бизнеса адрес?")


@router.message(BusinessReg.address)
async def business_reg_third(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(BusinessReg.contact_person)
    await message.answer("Как Вас зовут?")


@router.message(BusinessReg.contact_person)
async def business_reg_fourth(message: Message, state: FSMContext):
    await state.update_data(contact_person=message.text)
    await state.set_state(BusinessReg.contact_phone)
    await message.answer("Ваш номер телефона?")


@router.message(BusinessReg.contact_phone)
async def business_reg_fifth(message: Message, state: FSMContext):
    await state.update_data(contact_phone=message.text)
    data = await state.get_data()
    await message.answer(
        f"""Проверьте, все ли правильно?

<b>Название:</b> {data["business_name"]}
<b>Адрес:</b> {data["address"]}
<b>Контактное лицо:</b> {data["contact_person"]}
<b>Контактный телефон:</b> {data["contact_phone"]}""",
        parse_mode="HTML",
        reply_markup=kb.reg_done_business,
    )


# Подтверждение регистрации бизнеса
@router.callback_query(F.data == "reg_yes_business")
async def confirm_reg(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    await rq.add_business(
        business_name=data["business_name"],
        address=data["address"],
        contact_person=data["contact_person"],
        contact_phone=data["contact_phone"],
        user_id=data["user_id"],
    )
    await callback.message.edit_reply_markup()
    await callback.message.answer(
        "Ваш бизнес зарегистрирован", reply_markup=kb.main_business
    )
    await state.clear()


# Отмена регистрации бизнеса
@router.callback_query(F.data == "reg_no_business")
async def no_reg(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        "Регистрация отменена, хотите начать заново?", reply_markup=kb.business
    )
    await state.clear()


# Личный кабинет бизнеса
@router.message(F.text == "Личный кабинет бизнеса")
async def cabinet_business(message: Message):
    user_id = message.from_user.id
    business = await rq.get_business_by_user_id(user_id)
    active_count = await rq.get_business_deliveries_count(user_id, "В ожидании")
    total_count = (
        await rq.get_business_deliveries_count(user_id, "Принято курьером")
        + active_count
    )
    await message.answer(
        f"""Профиль бизнеса

<b>Бизнес:</b> {business.business_name}
<b>Активные заказы:</b> {active_count}
<b>Всего заказов:</b> {total_count}""",
        parse_mode="HTML",
        reply_markup=kb.business_profile,
    )


# Изменение профиля бизнеса
@router.callback_query(F.data == "edit_profile_business")
async def edit_profile_business(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id

    business = await rq.get_business_by_user_id(user_id)

    name = business.business_name
    address = business.address
    person = business.contact_person
    phone = business.contact_phone
    await callback.message.edit_text(
        f"""<b>Название:</b> {name}
<b>Адрес:</b> {address}
<b>Контактное лицо:</b> {person}
<b>Контактный телефон:</b> {phone}""",
        reply_markup=kb.business_edit_profile,
        parse_mode="HTML",
    )


# Переход назад в профиле бизнеса
@router.callback_query(F.data == "business_back")
async def business_back(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    business = await rq.get_business_by_user_id(user_id)
    active_count = await rq.get_business_deliveries_count(user_id, "В ожидании")
    total_count = (
        await rq.get_business_deliveries_count(user_id, "Принято курьером")
        + active_count
    )
    await callback.message.edit_text(
        f"""Профиль бизнеса

<b>Бизнес:</b> {business.business_name}
<b>Активные заказы:</b> {active_count}
<b>Всего заказов:</b> {total_count}""",
        parse_mode="HTML",
        reply_markup=kb.business_profile,
    )


# Изменение названия бизнеса
@router.callback_query(F.data == "business_change_name")
async def change_business_name(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(EditBusiness.edit_name)
    await callback.message.answer("Введите новое название")


@router.message(EditBusiness.edit_name)
async def update_business_name(message: Message, state: FSMContext):
    new_name = message.text
    user_id = message.from_user.id

    await rq.update_business_name(
        business_name=new_name,
        user_id=user_id,
    )

    await message.answer(
        f"<b>Новое название:</b> {new_name}",
        reply_markup=kb.main_business,
        parse_mode="HTML",
    )
    await state.clear()


# Изменение адреса бизнеса
@router.callback_query(F.data == "business_change_address")
async def change_business_address(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(EditBusiness.edit_address)
    await callback.message.answer("Введите новый адрес")


@router.message(EditBusiness.edit_address)
async def update_business_address(message: Message, state: FSMContext):
    new_address = message.text
    user_id = message.from_user.id

    await rq.update_business_address(
        business_address=new_address,
        user_id=user_id,
    )

    await message.answer(
        f"<b>Новый адрес:</b> {new_address}",
        reply_markup=kb.main_business,
        parse_mode="HTML",
    )
    await state.clear()


# Изменение контактного лица
@router.callback_query(F.data == "business_change_person")
async def change_business_person(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(EditBusiness.edit_contact_person)
    await callback.message.answer("Введите новое имя")


@router.message(EditBusiness.edit_contact_person)
async def update_business_person(message: Message, state: FSMContext):
    new_person = message.text
    user_id = message.from_user.id

    await rq.update_business_person(
        business_person=new_person,
        user_id=user_id,
    )

    await message.answer(
        f"<b>Новое имя:</b> {new_person}",
        reply_markup=kb.main_business,
        parse_mode="HTML",
    )
    await state.clear()


# Изменение контактного телефона
@router.callback_query(F.data == "business_change_phone")
async def change_business_phone(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(EditBusiness.edit_contact_phone)
    await callback.message.answer("Введите новый номер телефона")


@router.message(EditBusiness.edit_contact_phone)
async def update_business_phone(message: Message, state: FSMContext):
    new_phone = message.text
    user_id = message.from_user.id

    await rq.update_business_phone(
        business_phone=new_phone,
        user_id=user_id,
    )

    await message.answer(
        f"<b>Новый номер:</b> {new_phone}",
        reply_markup=kb.main_business,
        parse_mode="HTML",
    )
    await state.clear()


# Удаление профиля бизнеса
@router.callback_query(F.data == "delete_profile_business")
async def delete_business_profile(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        "Вы уверены, что хотите удалить свой профиль бизнеса?",
        reply_markup=kb.confirm_delete_business,
    )


# Подтверждение удаления бизнеса
@router.callback_query(F.data == "confirm_delete_business")
async def delete_business(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id

    await rq.delete_business_by_user_id(user_id)

    await callback.message.answer("Ваш профиль удален", reply_markup=kb.main)


# Отмена удаления бизнеса
@router.callback_query(F.data == "cancel_delete_business")
async def cancel_delete_business(callback: CallbackQuery):
    await callback.answer()

    await callback.message.answer(
        "Удаление профиля отменено", reply_markup=kb.main_business
    )


# Кнопка "Новая доставка"
@router.message(F.text == "Новая доставка")
async def business_delivery_first(message: Message, state: FSMContext):
    user_id = message.from_user.id
    business = await rq.get_business_by_user_id(user_id)

    await state.update_data(
        client_phone=business.contact_phone, start_geo=business.address
    )
    await state.set_state(BusinessDelivery.end_geo)
    await message.answer("Напишите адрес, куда доставить?")


@router.message(BusinessDelivery.end_geo)
async def business_delivery_second(message: Message, state: FSMContext):
    await state.update_data(end_geo=message.text)
    await state.set_state(BusinessDelivery.phone)
    await message.answer("Номер получателя для связи?")


@router.message(BusinessDelivery.phone)
async def business_delivery_third(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(BusinessDelivery.price)
    await message.answer("Сколько заплатите за доставку?")


@router.message(BusinessDelivery.price)
async def business_delivery_fourth(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.update_data(status="В ожидании")
    data = await state.get_data()

    await message.answer(
        f"""Проверьте, все ли правильно?

<b>Адрес доставки:</b> {data['end_geo']}
<b>Получатель:</b> {data["phone"]}
<b>Цена за доставку:</b> {data["price"]} рублей""",
        parse_mode="HTML",
        reply_markup=kb.fast_delivery,
    )


# Принятые заказы
@router.callback_query(F.data.startswith("business_deliveries"))
async def business_deliveries(callback: CallbackQuery):
    await callback.answer()

    if ":" in callback.data:
        data_parts = callback.data.split(":")
        page = int(data_parts[1].split("_")[0])
        status = (
            data_parts[1].split("_")[1]
            if len(data_parts[1].split("_")) > 1
            else "active"
        )
    else:
        page = 1
        status = callback.data.split("_")[-1]

    user_id = callback.from_user.id
    per_page = ORDER_PAGES

    if status == "active":
        status = "В ожидании"
    elif status == "done":
        status = "Принято курьером"

    deliveries = await rq.get_business_deliveries(user_id, page, per_page, status)

    if not deliveries:
        await callback.message.answer("История заказов пуста")
        return

    keyboard_builder = InlineKeyboardBuilder()

    for delivery in deliveries:
        button_text = f"Заказ №{delivery.id}"
        button_callback_data = f"order_detail:{delivery.id}"
        keyboard_builder.button(text=button_text, callback_data=button_callback_data)

    if page > 1:
        keyboard_builder.button(
            text="<< Назад", callback_data=f"business_deliveries:{page - 1}_{status}"
        )

    if len(deliveries) == per_page:
        next_deliveries = await rq.get_business_deliveries(
            user_id, page + 1, per_page, status
        )
        if next_deliveries:
            keyboard_builder.button(
                text="Вперед >>",
                callback_data=f"business_deliveries:{page + 1}_{status}",
            )

    keyboard_builder.button(text="Отмена", callback_data="business_back")

    keyboard_builder.adjust(2)

    keyboard = keyboard_builder.as_markup()

    if callback.message:
        await callback.message.edit_text("История заказов", reply_markup=keyboard)
