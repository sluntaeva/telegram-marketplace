from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔎 Смотреть"), KeyboardButton(text="➕ Продать")],
        [KeyboardButton(text="❤️ Избранное"), KeyboardButton(text="📦 Мои объявления")],
        [KeyboardButton(text="👤 Профиль")],
    ],
    resize_keyboard=True,
)
