from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from database import async_session
from database.models import Favorite, User, View
from keyboards.item import feed_keyboard
from services.feed import item_caption, next_unseen_item

router = Router()


async def send_next(message: Message, telegram_id: int) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        if user is None or not user.city:
            await message.answer("Сначала отправьте /start и выберите город.")
            return
        item = await next_unseen_item(session, user.id, user.city)
        if item is None:
            await message.answer("Пока новых объявлений нет.")
            return
        await message.answer_photo(item.photo_file_id, caption=item_caption(item), reply_markup=feed_keyboard(item.id, item.seller.username))


@router.message(F.text == "🔎 Смотреть")
async def browse(message: Message) -> None:
    await send_next(message, message.from_user.id)


@router.callback_query(F.data.startswith("feed:"))
async def feed_action(callback: CallbackQuery) -> None:
    _, action, raw_id = callback.data.split(":")
    item_id = int(raw_id)
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == callback.from_user.id))
        if user is None:
            await callback.answer("Сначала отправьте /start", show_alert=True)
            return
        await session.execute(insert(View).values(user_id=user.id, item_id=item_id).on_conflict_do_nothing())
        if action == "save":
            await session.execute(insert(Favorite).values(user_id=user.id, item_id=item_id).on_conflict_do_nothing())
        await session.commit()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer("Сохранено" if action == "save" else None)
    await send_next(callback.message, callback.from_user.id)


@router.callback_query(F.data == "seller:unavailable")
async def seller_unavailable(callback: CallbackQuery) -> None:
    await callback.answer("У продавца нет публичного имени пользователя Telegram, поэтому связаться с ним напрямую пока нельзя.", show_alert=True)
