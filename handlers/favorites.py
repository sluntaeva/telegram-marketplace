from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy import delete, select
from sqlalchemy.orm import joinedload

from database import async_session
from database.models import Favorite, Item, User
from keyboards.item import favorite_keyboard
from services.feed import item_caption

router = Router()


async def send_favorite(message: Message, telegram_id: int, after_id: int = 0) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        if user is None:
            await message.answer("Сначала отправьте /start.")
            return
        query = (select(Item).join(Favorite).options(joinedload(Item.seller))
                 .where(Favorite.user_id == user.id, Item.is_active.is_(True), Item.id > after_id)
                 .order_by(Item.id).limit(1))
        item = await session.scalar(query)
        if item is None and after_id:
            item = await session.scalar((select(Item).join(Favorite).options(joinedload(Item.seller))
                .where(Favorite.user_id == user.id, Item.is_active.is_(True)).order_by(Item.id).limit(1)))
        if item is None:
            await message.answer("В избранном пока нет объявлений.")
            return
        await message.answer_photo(item.photo_file_id, caption=item_caption(item), reply_markup=favorite_keyboard(item.id, item.seller.username))


@router.message(F.text == "❤️ Избранное")
async def favorites(message: Message) -> None:
    await send_favorite(message, message.from_user.id)


@router.callback_query(F.data.startswith("favorite:"))
async def favorite_action(callback: CallbackQuery) -> None:
    _, action, raw_id = callback.data.split(":")
    item_id = int(raw_id)
    if action == "remove":
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.telegram_id == callback.from_user.id))
            if user:
                await session.execute(delete(Favorite).where(Favorite.user_id == user.id, Favorite.item_id == item_id))
                await session.commit()
        await callback.answer("Удалено")
    else:
        await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await send_favorite(callback.message, callback.from_user.id, item_id)
