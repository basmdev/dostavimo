from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


# Главная клавиатура
main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Срочная доставка')],
    [KeyboardButton(text='Я предприниматель')],
    [KeyboardButton(text='Я курьер')],
    [KeyboardButton(text='Помощь')]
],
     resize_keyboard=True)

main_business = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Личный кабинет')],
    [KeyboardButton(text='Помощь')]
],
     resize_keyboard=True)

# Регистрация бизнеса
business = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='business_yes'),
     InlineKeyboardButton(text='Нет', callback_data='business_no')]
])

# Регистрация курьера
courier = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='courier_yes'),
     InlineKeyboardButton(text='Нет', callback_data='courier_no')]
])

# Подтверждение регистрации
reg_done = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='reg_yes'),
     InlineKeyboardButton(text='Нет', callback_data='reg_no')]
])