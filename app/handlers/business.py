from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.database.requests as rq


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


# Пункт меню "Я предприниматель"
@router.message(F.text == "Я предприниматель")
async def business(message: Message):
    await message.answer("Желаете пройти регистрацию?", reply_markup=kb.business)


# Кнопка отмены регистрации бизнеса
@router.callback_query(F.data == "business_no")
async def business_reg_first(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()


# Кнопка регистрации бизнеса
@router.callback_query(F.data == "business_yes")
async def business_reg_first(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    await state.update_data(user_id=user_id)
    await state.set_state(BusinessReg.business_name)
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
    await callback.message.answer(
        "Регистрация прошла успешно", reply_markup=kb.main_business
    )
    await state.clear()


# Отмена регистрации бизнеса
@router.callback_query(F.data == "reg_no_business")
async def no_reg(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        "Регистрация отменена, хотите начать заново?", reply_markup=kb.business
    )
    await state.clear()


# Личный кабинет бизнеса
@router.message(F.text == "Личный кабинет бизнеса")
async def cabinet_business(message: Message):
    await message.answer("Личный кабинет бизнеса", reply_markup=kb.business_profile)


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
async def edit_profile_business(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "Личный кабинет бизнеса", reply_markup=kb.business_profile
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
