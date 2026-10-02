from decimal import Decimal, InvalidOperation

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, Message, ReplyKeyboardMarkup
from sqlalchemy import select

from database import async_session
from database.models import Item, User
from keyboards.menu import main_menu
from services.feed import item_caption
from states.listing import ListingForm

router = Router()
CATEGORIES = ("Электроника", "Одежда", "Дом", "Хобби", "Авто", "Другое")
CITIES = ("Санкт-Петербург", "Москва", "Новосибирск", "Другой")


def choices(values: tuple[str, ...]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=value)] for value in values], resize_keyboard=True, one_time_keyboard=True)


@router.message(F.text == "➕ Продать")
async def sell(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(ListingForm.title)
    await message.answer("Введите название товара (до 120 символов):")


@router.message(ListingForm.title)
async def title(message: Message, state: FSMContext) -> None:
    value = (message.text or "").strip()
    if not value or len(value) > 120:
        await message.answer("Название должно содержать от 1 до 120 символов. Попробуйте ещё раз:")
        return
    await state.update_data(title=value)
    await state.set_state(ListingForm.price)
    await message.answer("Введите цену больше нуля, например 1499,99:")


@router.message(ListingForm.price)
async def price(message: Message, state: FSMContext) -> None:
    try:
        value = Decimal((message.text or "").strip().replace(",", "."))
        if value <= 0 or value > Decimal("9999999999.99"):
            raise InvalidOperation
        value = value.quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        await message.answer("Введите корректное положительное число:")
        return
    await state.update_data(price=str(value))
    await state.set_state(ListingForm.category)
    await message.answer("Выберите категорию:", reply_markup=choices(CATEGORIES))


@router.message(ListingForm.category)
async def category(message: Message, state: FSMContext) -> None:
    if message.text not in CATEGORIES:
        await message.answer("Выберите категорию с помощью кнопок.", reply_markup=choices(CATEGORIES))
        return
    await state.update_data(category=message.text)
    await state.set_state(ListingForm.description)
    await message.answer("Введите описание (до 1000 символов):", reply_markup=main_menu)


@router.message(ListingForm.description)
async def description(message: Message, state: FSMContext) -> None:
    value = (message.text or "").strip()
    if not value or len(value) > 1000:
        await message.answer("Описание должно содержать от 1 до 1000 символов. Попробуйте ещё раз:")
        return
    await state.update_data(description=value)
    await state.set_state(ListingForm.photo)
    await message.answer("Отправьте одну фотографию товара:")


@router.message(ListingForm.photo, F.photo)
async def photo(message: Message, state: FSMContext) -> None:
    await state.update_data(photo_file_id=message.photo[-1].file_id)
    await state.set_state(ListingForm.city)
    await message.answer("Выберите город объявления:", reply_markup=choices(CITIES))


@router.message(ListingForm.photo)
async def invalid_photo(message: Message) -> None:
    await message.answer("Отправьте фотографию, а не файл или текст.")


@router.message(ListingForm.city)
async def city(message: Message, state: FSMContext) -> None:
    if message.text not in CITIES:
        await message.answer("Выберите город с помощью кнопок.", reply_markup=choices(CITIES))
        return
    await state.update_data(city=message.text)
    data = await state.get_data()
    preview = Item(seller_id=0, **data)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Опубликовать", callback_data="listing:publish"),
        InlineKeyboardButton(text="Отмена", callback_data="listing:cancel"),
    ]])
    await state.set_state(ListingForm.preview)
    await message.answer_photo(data["photo_file_id"], caption="<b>Предпросмотр</b>\n\n" + item_caption(preview), reply_markup=keyboard)


@router.callback_query(ListingForm.preview, F.data == "listing:publish")
async def publish(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == callback.from_user.id))
        if user is None:
            await callback.answer("Сначала отправьте /start", show_alert=True)
            return
        session.add(Item(seller_id=user.id, title=data["title"], price=Decimal(data["price"]), category=data["category"],
                         description=data["description"], photo_file_id=data["photo_file_id"], city=data["city"], is_active=True))
        await session.commit()
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Объявление опубликовано.", reply_markup=main_menu)
    await callback.answer()


@router.callback_query(ListingForm.preview, F.data == "listing:cancel")
async def cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Создание объявления отменено.", reply_markup=main_menu)
    await callback.answer()
