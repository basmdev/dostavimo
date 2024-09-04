from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


# Главная клавиатура
main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Срочная доставка")],
        [KeyboardButton(text="Я предприниматель")],
        [KeyboardButton(text="Я курьер")],
        [KeyboardButton(text="Помощь")],
    ],
    resize_keyboard=True,
)

# Клавиатура предпринимателя
main_business = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Личный кабинет")], [KeyboardButton(text="Помощь")]],
    resize_keyboard=True,
)

# Клавиатура курьера
main_courier = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Личный кабинет")], [KeyboardButton(text="Помощь")]],
    resize_keyboard=True,
)

# Регистрация бизнеса
business = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="business_yes"),
            InlineKeyboardButton(text="Нет", callback_data="business_no"),
        ]
    ]
)

# Регистрация курьера
courier = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="courier_yes"),
            InlineKeyboardButton(text="Нет", callback_data="courier_no"),
        ]
    ]
)

# Подтверждение регистрации бизнеса
reg_done_business = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="reg_yes_business"),
            InlineKeyboardButton(text="Нет", callback_data="reg_no_business"),
        ]
    ]
)

# Подтверждение регистрации курьера
reg_done_courier = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="reg_yes_courier"),
            InlineKeyboardButton(text="Нет", callback_data="reg_no_courier"),
        ]
    ]
)

# Подтверждение быстрой доставки
fast_delivery = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="delivery_yes"),
            InlineKeyboardButton(text="Нет", callback_data="delivery_no"),
        ]
    ]
)

# Информация о доставке для курьера
delivery_action = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Принять", callback_data="accept_delivery"),
            InlineKeyboardButton(text="Отклонить", callback_data="decline_delivery"),
        ],
        [
            InlineKeyboardButton(
                text="Сообщить о нарушении", callback_data="report_violation"
            )
        ],
    ]
)
