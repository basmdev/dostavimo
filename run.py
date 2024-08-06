import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from config import TOKEN


bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    await dp.start_polling(bot)

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Привет!')

@dp.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('Это команда HELP')

@dp.message(F.text == 'Как дела?')
async def how_are_you(message: Message):
    await message.answer('Все хорошо!')

if __name__ == '__main__':
    asyncio.run(main())