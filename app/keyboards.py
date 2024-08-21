from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Срочная доставка')],
    [KeyboardButton(text='Я предприниматель')],
    [KeyboardButton(text='Я курьер')],
    [KeyboardButton(text='Помощь')]
],
     resize_keyboard=True,
     input_field_placeholder='Выберите...')

business = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='business_yes'),
     InlineKeyboardButton(text='Нет', callback_data='business_no')]
])

courier = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='courier_yes'),
     InlineKeyboardButton(text='Нет', callback_data='courier_no')]
])