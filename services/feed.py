from html import escape
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database.models import Item, View


async def next_unseen_item(session: AsyncSession, user_id: int, city: str | None = None) -> Item | None:
    viewed = select(View.item_id).where(View.user_id == user_id)
    query = select(Item).options(joinedload(Item.seller)).where(
        Item.is_active.is_(True), Item.seller_id != user_id, Item.id.not_in(viewed)
    )
    if city and city != "Другой":
        query = query.where(Item.city == city)
    return await session.scalar(query.order_by(Item.created_at.desc()).limit(1))


def item_caption(item: Item) -> str:
    # During listing preview the FSM still stores the validated price as text.
    # Persisted listings return Decimal, so normalize both forms here.
    price_value = Decimal(str(item.price))
    price = f"{price_value:,.2f}".rstrip("0").rstrip(".").replace(",", " ")
    return (
        f"<b>{escape(item.title)}</b>\n"
        f"💰 {price}\n📍 {escape(item.city)}\n🏷 {escape(item.category)}\n\n{escape(item.description)}"
    )
