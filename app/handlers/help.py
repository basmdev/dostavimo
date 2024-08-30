from aiogram import F, Router
from aiogram.types import Message

router = Router()


# Пункт меню "Помощь"
@router.message(F.text == "Помощь")
async def help(message: Message):
    await message.answer("Выбрана помощь")
