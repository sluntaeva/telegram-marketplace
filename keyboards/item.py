from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def feed_keyboard(item_id: int, seller_username: str | None) -> InlineKeyboardMarkup:
    seller = (
        InlineKeyboardButton(text="💬 Продавец", url=f"https://t.me/{seller_username}")
        if seller_username
        else InlineKeyboardButton(text="💬 Продавец", callback_data="seller:unavailable")
    )
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❤️ Сохранить", callback_data=f"feed:save:{item_id}"),
         InlineKeyboardButton(text="➡️ Дальше", callback_data=f"feed:next:{item_id}")],
        [seller],
    ])


def favorite_keyboard(item_id: int, seller_username: str | None) -> InlineKeyboardMarkup:
    seller = (
        InlineKeyboardButton(text="💬 Продавец", url=f"https://t.me/{seller_username}")
        if seller_username
        else InlineKeyboardButton(text="💬 Продавец", callback_data="seller:unavailable")
    )
    return InlineKeyboardMarkup(inline_keyboard=[
        [seller, InlineKeyboardButton(text="🗑 Удалить", callback_data=f"favorite:remove:{item_id}")],
        [InlineKeyboardButton(text="➡️ Следующее", callback_data=f"favorite:next:{item_id}")],
    ])


def owner_keyboard(item_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Снять с публикации", callback_data=f"owner:deactivate:{item_id}")],
        [InlineKeyboardButton(text="➡️ Следующее", callback_data=f"owner:next:{item_id}")],
    ])
