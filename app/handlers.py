from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb


router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Привет!', reply_markup=kb.main)

@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('Это команда HELP')

@router.message(F.text == 'Как дела?')
async def how_are_you(message: Message):
    await message.answer('Все хорошо!')

@router.callback_query(F.data == 'catalog')
async def catalog(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text('Привет, колбэк!', reply_markup=await kb.inline_cars())