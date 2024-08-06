from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

import app.keyboards as kb


router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Привет!', reply_markup=await kb.inline_cars())

@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('Это команда HELP')

@router.message(F.text == 'Как дела?')
async def how_are_you(message: Message):
    await message.answer('Все хорошо!')