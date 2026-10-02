from aiogram import Dispatcher

from . import favorites, feed, profile, sell, start


def register_routers(dispatcher: Dispatcher) -> None:
    dispatcher.include_routers(start.router, sell.router, feed.router, favorites.router, profile.router)
