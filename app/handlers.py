from datetime import datetime

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State

import app.keyboards as kb
import app.database.requests as rq


router = Router()

class Reg(StatesGroup):
    name = State()
    number = State()

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