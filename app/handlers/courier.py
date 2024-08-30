from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.database.requests as rq


router = Router()


class CourierReg(StatesGroup):
    courier_name = State()
    contact_phone = State()
    photo_url = State()


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
        "Регистрация прошла успешно!", reply_markup=kb.main_courier
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
