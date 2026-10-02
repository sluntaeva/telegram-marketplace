from html import escape

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from database import async_session
from database.models import Item, User
from handlers.start import CITIES, city_keyboard
from keyboards.item import owner_keyboard
from services.feed import item_caption

router = Router()


@router.message(F.text == "👤 Профиль")
async def profile(message: Message) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
        if user is None:
            await message.answer("Сначала отправьте /start.")
            return
        count = await session.scalar(select(func.count(Item.id)).where(Item.seller_id == user.id, Item.is_active.is_(True)))
    username = f"@{user.username}" if user.username else "не задано"
    await message.answer(
        f"<b>{escape(user.first_name)}</b>\nИмя пользователя: {escape(username)}\nГород: {escape(user.city or 'не выбран')}\nАктивных объявлений: {count}",
        reply_markup=city_keyboard("profile_city"),
    )


@router.callback_query(F.data.startswith("profile_city:"))
async def change_city(callback: CallbackQuery) -> None:
    city = callback.data.split(":", 1)[1]
    if city not in CITIES:
        await callback.answer("Неизвестный город", show_alert=True)
        return
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == callback.from_user.id))
        if user:
            user.city = city
            await session.commit()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"Город в профиле изменён на: {city}.")
    await callback.answer()


async def send_own(message: Message, telegram_id: int, after_id: int = 0) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        if user is None:
            await message.answer("Сначала отправьте /start.")
            return
        query = (select(Item).options(joinedload(Item.seller))
                 .where(Item.seller_id == user.id, Item.is_active.is_(True), Item.id > after_id)
                 .order_by(Item.id).limit(1))
        item = await session.scalar(query)
        if item is None and after_id:
            item = await session.scalar(select(Item).options(joinedload(Item.seller))
                .where(Item.seller_id == user.id, Item.is_active.is_(True)).order_by(Item.id).limit(1))
        if item is None:
            await message.answer("У вас нет активных объявлений.")
            return
        await message.answer_photo(item.photo_file_id, caption=item_caption(item), reply_markup=owner_keyboard(item.id))


@router.message(F.text == "📦 Мои объявления")
async def my_listings(message: Message) -> None:
    await send_own(message, message.from_user.id)


@router.callback_query(F.data.startswith("owner:"))
async def owner_action(callback: CallbackQuery) -> None:
    _, action, raw_id = callback.data.split(":")
    item_id = int(raw_id)
    if action == "deactivate":
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.telegram_id == callback.from_user.id))
            item = await session.scalar(select(Item).where(Item.id == item_id, Item.seller_id == user.id)) if user else None
            if item:
                item.is_active = False
                await session.commit()
        await callback.answer("Снято с публикации")
    else:
        await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await send_own(callback.message, callback.from_user.id, item_id)
