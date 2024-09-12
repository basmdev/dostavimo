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
    keyboard=[
        [KeyboardButton(text="Личный кабинет бизнеса")],
        [KeyboardButton(text="Помощь")],
    ],
    resize_keyboard=True,
)

# Клавиатура курьера
main_courier = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Личный кабинет курьера")],
        [KeyboardButton(text="Помощь")],
    ],
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


# # Информация о доставке для курьера
def get_delivery_action_keyboard(delivery_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Принять", callback_data=f"accept_delivery_{delivery_id}"
                ),
                InlineKeyboardButton(
                    text="Отклонить", callback_data=f"decline_delivery_{delivery_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Сообщить о нарушении",
                    callback_data=f"report_violation_{delivery_id}",
                )
            ],
        ]
    )
    return keyboard


# Личный кабинет бизнеса
business_profile = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Мои доставки", callback_data="business_deliveries"
            )
        ],
        [
            InlineKeyboardButton(
                text="Редактировать профиль", callback_data="edit_profile_business"
            )
        ],
        [
            InlineKeyboardButton(
                text="Удалить профиль", callback_data="delete_profile_business"
            )
        ],
    ]
)

# Личный кабинет курьера
courier_profile = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Принятые заказы", callback_data="courier_deliveries"
            )
        ],
        [
            InlineKeyboardButton(
                text="Редактировать профиль", callback_data="edit_profile_courier"
            )
        ],
        [
            InlineKeyboardButton(
                text="Удалить профиль", callback_data="delete_profile_courier"
            )
        ],
    ]
)

# Редактирование профиля бизнеса
business_edit_profile = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Изменить название", callback_data="business_change_name"
            )
        ],
        [
            InlineKeyboardButton(
                text="Изменить адрес", callback_data="business_change_address"
            )
        ],
        [
            InlineKeyboardButton(
                text="Изменить контактное лицо", callback_data="business_change_person"
            )
        ],
        [
            InlineKeyboardButton(
                text="Изменить контактный телефон",
                callback_data="business_change_phone",
            )
        ],
        [InlineKeyboardButton(text="Отмена", callback_data="business_back")],
    ]
)

# Редактирование профиля курьера
courier_edit_profile = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Изменить контактный телефон",
                callback_data="courier_change_phone",
            )
        ],
        [InlineKeyboardButton(text="Отмена", callback_data="courier_back")],
    ]
)

# Подтверждение удаления профиля бизнеса
confirm_delete_business = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Подтвердить", callback_data="confirm_delete_business"
            ),
            InlineKeyboardButton(
                text="Отменить", callback_data="cancel_delete_business"
            ),
        ]
    ]
)

# Подтверждение удаления профиля курьера
confirm_delete_courier = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Подтвердить", callback_data="confirm_delete_courier"
            ),
            InlineKeyboardButton(
                text="Отменить", callback_data="cancel_delete_courier"
            ),
        ]
    ]
)
