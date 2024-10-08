from datetime import datetime

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

import app.database.requests as rq
import app.keyboards as kb
from app.database.models import async_session

router = Router()


# Приветственное сообщение
@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    async with async_session() as session:
        await rq.add_user(
            tg_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            last_interaction=datetime.now(),
        )
        has_business = await rq.get_user_has_business(user.id)
        is_courier = await rq.get_user_is_courier(user.id)

        reply_markup = (
            kb.main_business
            if has_business
            else (kb.main_courier if is_courier else kb.main)
        )

        await message.answer("Добро пожаловать в Dostavimo!", reply_markup=reply_markup)
