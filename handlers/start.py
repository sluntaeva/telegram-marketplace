from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy import select

from database import async_session
from database.models import User
from keyboards.menu import main_menu

router = Router()
CITIES = ("Санкт-Петербург", "Москва", "Новосибирск", "Другой")


def city_keyboard(prefix: str = "city") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=city, callback_data=f"{prefix}:{city}")] for city in CITIES
    ])


@router.message(CommandStart())
async def start(message: Message) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
        if user is None:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name or "Пользователь Telegram",
            )
            session.add(user)
        else:
            user.username = message.from_user.username
            user.first_name = message.from_user.first_name or user.first_name
        await session.commit()
        has_city = bool(user.city)
    if not has_city:
        await message.answer("Добро пожаловать! Выберите ваш город:", reply_markup=city_keyboard())
    else:
        await message.answer("С возвращением!", reply_markup=main_menu)


@router.callback_query(F.data.startswith("city:"))
async def select_city(callback: CallbackQuery) -> None:
    city = callback.data.split(":", 1)[1]
    if city not in CITIES:
        await callback.answer("Неизвестный город", show_alert=True)
        return
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == callback.from_user.id))
        if user is None:
            await callback.answer("Сначала отправьте /start", show_alert=True)
            return
        user.city = city
        await session.commit()
    await callback.message.edit_text(f"Выбран город: {city}")
    await callback.message.answer("Главное меню", reply_markup=main_menu)
    await callback.answer()
