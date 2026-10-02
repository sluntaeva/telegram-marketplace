# Telegram Marketplace — Beta 0.1

A small local marketplace bot with card-by-card listing browsing. Users choose a city, publish one-photo listings, browse unseen listings, save favorites, contact sellers through Telegram, manage their own listings, and view a profile.

## Technology stack

- Python 3.12+
- aiogram 3 (long polling)
- PostgreSQL
- SQLAlchemy 2 async ORM
- asyncpg
- python-dotenv

## Project structure

```text
telegram-marketplace/
├── app.py                 # application entry point
├── config.py              # environment configuration
├── handlers/              # Telegram commands, messages, and callbacks
├── keyboards/             # reply and inline keyboards
├── database/              # async engine and ORM models
├── services/              # feed selection and listing formatting
└── states/                # listing creation FSM
```

The database contains `users`, `items`, `favorites`, and `views`. Foreign keys connect listings to sellers and saved/viewed records to users and listings. Unique constraints prevent duplicate favorites and views. On startup, SQLAlchemy creates missing tables. This automatic initialization is suitable for Beta 0.1; use Alembic before making schema changes in a deployed system.

## 1. Create the PostgreSQL database

Install PostgreSQL and remember the password chosen for the `postgres` user. In PowerShell, create the database (adjust the PostgreSQL version/path if needed):

```powershell
& "C:\Program Files\PostgreSQL\16\bin\createdb.exe" -U postgres telegram_marketplace
```

If `createdb` is already on PATH:

```powershell
createdb -U postgres telegram_marketplace
```

## 2. Create the Telegram bot with BotFather

1. Open Telegram and start a chat with the verified `@BotFather` account.
2. Send `/newbot`.
3. Choose a display name and a unique username ending in `bot`.
4. Copy the API token. Keep it private and revoke it through BotFather if it is exposed.

## 3. Configure environment variables

From this project directory:

```powershell
Copy-Item .env.example .env
notepad .env
```

Set both values:

```dotenv
BOT_TOKEN=the_token_from_BotFather
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/telegram_marketplace
```

URL-encode special characters in the database password (for example, `@` becomes `%40`). The real `.env` file is ignored by Git.

## 4. Install and run

```powershell
Set-Location telegram-marketplace
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

If PowerShell blocks virtual-environment activation for this session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

The first launch tests the PostgreSQL connection and creates all tables. A connection or credentials problem is logged and stops startup, making configuration errors visible.

## 5. Test Beta 0.1

Use two Telegram accounts so one account can browse the other account's listing.

1. Send `/start` from both accounts and choose the same city.
2. With account A, choose **➕ Sell** and complete every prompt. Test that text sent at the photo step is rejected, and publish the preview.
3. With account B, choose **🔎 Browse**. Confirm the photo and details appear and account B's own listings do not.
4. Test **➡️ Next** and **❤️ Save**. A viewed item should not return to the feed, and saving twice cannot create a duplicate.
5. Open **❤️ Favorites**, move through saved items, remove one, and test **💬 Seller**. Contact opens `t.me/<username>` only when the seller has a public username.
6. With account A, open **📦 My listings** and deactivate the listing. It should disappear from active listings and other users' feeds/favorites.
7. Open **👤 Profile**, verify the active listing count, and change the city.

Stop the bot with `Ctrl+C`.

## Beta limitations

There are no payments, delivery, reviews, ratings, recommendations, maps, advanced search, web UI, Mini App, admin dashboard, promotion, editing, or multiple listing photos in this release.
