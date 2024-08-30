from datetime import datetime

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.database.crud import get_user_has_business, get_user_is_courier
import app.keyboards as kb
import app.database.requests as rq
from app.database.models import async_session


router = Router()

class BusinessReg(StatesGroup):
    business_name = State()
    address = State()
    contact_person = State()
    contact_phone = State()


class CourierReg(StatesGroup):
    courier_name = State()
    contact_phone = State()
    photo_url = State()


class FastDelivery(StatesGroup):
    start_geo = State()
    end_geo = State()
    name = State()
    phone = State()
    comment = State()


class GeoState(StatesGroup):
    waiting_for_address = State()

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
            last_interaction=datetime.now()
        )
        has_business = await get_user_has_business(user.id, session)
        is_courier = await get_user_is_courier(user.id, session)

        reply_markup = kb.main_business if has_business else (kb.main_courier if is_courier else kb.main)

        await message.answer('Добро пожаловать в Dostavimo!', reply_markup=reply_markup)

# Пункт меню "Срочная доставка"
@router.message(F.text == 'Срочная доставка')
async def delivery_first(message: Message, state: FSMContext):
    await state.set_state(FastDelivery.start_geo)
    await message.answer('Укажите адрес, откуда забирать?')

@router.message(FastDelivery.start_geo)
async def delivery_second(message: Message, state: FSMContext):
    await state.update_data(start_geo=message.text)
    await state.set_state(FastDelivery.end_geo)
    await message.answer('Укажите адрес, куда доставить?')

@router.message(FastDelivery.end_geo)
async def delivery_third(message: Message, state: FSMContext):
    await state.update_data(end_geo=message.text)
    await state.set_state(FastDelivery.name)
    await message.answer('Имя получателя?')

@router.message(FastDelivery.name)
async def delivery_fourth(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(FastDelivery.phone)
    await message.answer('Номер телефона получателя?')

@router.message(FastDelivery.phone)
async def delivery_fourth(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(FastDelivery.comment)
    await message.answer('Укажите комментарий к заказу')

@router.message(FastDelivery.comment)
async def delivery_fifth(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    data = await state.get_data()

    await message.answer(
    f'''Проверьте, все ли правильно?
<b>Начальный адрес:</b> {data['start_geo']}
<b>Адрес доставки:</b> {data['end_geo']}
<b>Имя получателя:</b> {data["name"]}
<b>Номер телефона получателя:</b> {data["phone"]}
<b>Комментарий:</b> {data['comment']}''',
    parse_mode="HTML",
    reply_markup=kb.fast_delivery
)

@router.callback_query(F.data == 'delivery_yes')
async def confirm_delivery(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()

    await rq.add_delivery(
        start_geo=data['start_geo'],
        end_geo=data['end_geo'],
        name=data['name'],
        phone=data['phone'],
        comment=data['comment']
    )

    await callback.message.answer('Информация отправлена курьерам, ждите', reply_markup=kb.main)
    await state.clear()

# Отмена срочной доставки
@router.callback_query(F.data == 'delivery_no')
async def no_delivery(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Доставка отменена', reply_markup=kb.main)
    await state.clear()

# Пункт меню "Я предприниматель"
@router.message(F.text == 'Я предприниматель')
async def business(message: Message):
    await message.answer('Желаете пройти регистрацию?', reply_markup=kb.business)

# Пункт меню "Я курьер"
@router.message(F.text == 'Я курьер')
async def courier(message: Message):
    await message.answer('Желаете пройти регистрацию?', reply_markup=kb.courier)

# Пункт меню "Помощь"
@router.message(F.text == 'Помощь')
async def help(message: Message):
    await message.answer('Выбрана помощь')

# Кнопка отмены регистрации бизнеса
@router.callback_query(F.data == 'business_no')
async def business_reg_first(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()

# Кнопка отмены регистрации курьера
@router.callback_query(F.data == 'courier_no')
async def business_reg_first(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()

# Кнопка регистрации бизнеса
@router.callback_query(F.data == 'business_yes')
async def business_reg_first(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    await state.update_data(user_id=user_id)
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
async def business_reg_fifth(message: Message, state: FSMContext):
    await state.update_data(contact_phone=message.text)
    data = await state.get_data()
    await message.answer(
    f'''Проверьте, все ли правильно?
<b>Название:</b> {data["business_name"]}
<b>Адрес:</b> {data["address"]}
<b>Контактное лицо:</b> {data["contact_person"]}
<b>Контактный телефон:</b> {data["contact_phone"]}''',
    parse_mode="HTML",
    reply_markup=kb.reg_done_business
)
    
# Кнопка регистрации курьера
@router.callback_query(F.data == 'courier_yes')
async def courier_reg_first(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    await state.update_data(user_id=user_id)
    await state.set_state(CourierReg.courier_name)
    await callback.message.answer('Как Вас зовут?')

@router.message(CourierReg.courier_name)
async def courier_reg_second(message: Message, state: FSMContext):
    await state.update_data(courier_name=message.text)
    await state.set_state(CourierReg.contact_phone)
    await message.answer('Ваш номер телефона?')

@router.message(CourierReg.contact_phone)
async def courier_reg_third(message: Message, state: FSMContext):
    await state.update_data(contact_phone=message.text)
    await state.set_state(CourierReg.photo_url)
    await message.answer('Отправьте фото своего паспорта')

@router.message(CourierReg.photo_url)
async def courier_reg_fourth(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer('Пожалуйста, отправьте фото паспорта')
        return

    photo_id = message.photo[-1].file_id
    
    photo = await message.bot.get_file(photo_id)
    
    user_id = message.from_user.id
    
    file_name = f'photos/{user_id}.jpg'
    
    await message.bot.download_file(photo.file_path, file_name)

    await state.update_data(photo_url=file_name)

    data = await state.get_data()
    await message.answer(
        f'''Проверьте, все ли правильно:
<b>Имя:</b> {data["courier_name"]}
<b>Телефон:</b> {data["contact_phone"]}''',
        parse_mode="HTML",
        reply_markup=kb.reg_done_courier
    )

# Подтверждение регистрации курьера
@router.callback_query(F.data == 'reg_yes_courier')
async def confirm_reg(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    await rq.add_courier(
        courier_name=data["courier_name"],
        contact_phone=data["contact_phone"],
        photo_url=data['photo_url'],
        user_id=data["user_id"]
    )
    await callback.message.answer('Регистрация прошла успешно!', reply_markup=kb.main_courier)
    await state.clear()

# Подтверждение регистрации бизнеса
@router.callback_query(F.data == 'reg_yes_business')
async def confirm_reg(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    await rq.add_business(
        business_name=data["business_name"],
        address=data["address"],
        contact_person=data["contact_person"],
        contact_phone=data["contact_phone"],
        user_id=data["user_id"]
    )
    await callback.message.answer('Регистрация прошла успешно!', reply_markup=kb.main_business)
    await state.clear()

# Отмена регистрации бизнеса
@router.callback_query(F.data == 'reg_no_business')
async def no_reg(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Регистрация отменена, хотите начать заново?', reply_markup=kb.business)
    await state.clear()

# Отмена регистрации курьера
@router.callback_query(F.data == 'reg_no_courier')
async def no_reg(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Регистрация отменена, хотите начать заново?', reply_markup=kb.courier)
    await state.clear()