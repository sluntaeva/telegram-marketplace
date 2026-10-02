import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    bot_token: str
    database_url: str


def load_settings() -> Settings:
    load_dotenv()
    token = os.getenv("BOT_TOKEN", "").strip()
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not token:
        raise RuntimeError("Не указан BOT_TOKEN. Скопируйте .env.example в .env и добавьте токен.")
    if not database_url:
        raise RuntimeError("Не указан DATABASE_URL. Скопируйте .env.example в .env и добавьте адрес базы данных.")
    return Settings(bot_token=token, database_url=database_url)
