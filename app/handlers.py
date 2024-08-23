from datetime import datetime

from aiogram import F, Router
from aiogram.filters import CommandStart
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

@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    await rq.add_user(
        tg_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        last_interaction=datetime.now()
    )
    await message.answer('Добро пожаловать в Dostavimo!', reply_markup=kb.main)

@router.message(F.text == 'Срочная доставка')
async def catalog(message: Message):
    await message.answer('Выбрана срочная доставка')

@router.message(F.text == 'Я предприниматель')
async def catalog(message: Message):
    await message.answer('Желаете пройти регистрацию?', reply_markup=kb.business)

@router.message(F.text == 'Я курьер')
async def catalog(message: Message):
    await message.answer('Желаете пройти регистрацию?', reply_markup=kb.courier)

@router.message(F.text == 'Помощь')
async def catalog(message: Message):
    await message.answer('Выбрана помощь')

@router.callback_query(F.data == 'business_no')
async def business_reg_first(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()

@router.callback_query(F.data == 'business_yes')
async def business_reg_first(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(BusinessReg.business_name)
    await callback.message.answer('Как называется Ваш бизнес?')

@router.message(BusinessReg.business_name)
async def business_reg_second(message: Message, state: FSMContext):
    await state.update_data(business_name=message.text)
    await state.set_state(BusinessReg.address)
    await message.answer('Какой у Вашего бизнеса адрес?')

@router.message(BusinessReg.address)
async def business_reg_third(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(BusinessReg.contact_person)
    await message.answer('Как Вас зовут?')

@router.message(BusinessReg.contact_person)
async def business_reg_fourth(message: Message, state: FSMContext):
    await state.update_data(contact_person=message.text)
    await state.set_state(BusinessReg.contact_phone)
    await message.answer('Ваш номер телефона?')

@router.message(BusinessReg.contact_phone)
async def business_reg_fourth(message: Message, state: FSMContext):
    await state.update_data(contact_phone=message.text)
    data = await state.get_data()
    await message.answer(
    f'''Проверьте, все ли правильно?
<b>Название:</b> {data["business_name"]}
<b>Адрес:</b> {data["address"]}
<b>Контактное лицо:</b> {data["contact_person"]}
<b>Контактный телефон:</b> {data["contact_phone"]}''',
    parse_mode="HTML",
    reply_markup=kb.reg_done
)

@router.callback_query(F.data == 'reg_yes')
async def confirm_reg(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    await rq.add_business(
        business_name=data["business_name"],
        address=data["address"],
        contact_person=data["contact_person"],
        contact_phone=data["contact_phone"]
    )
    await callback.message.answer('Регистрация прошла успешно!')
    await state.clear()

@router.callback_query(F.data == 'reg_no')
async def no_reg(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Регистрация отменена, хотите начать заново?', reply_markup=kb.business)
    await state.clear()