import os

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Telegram BotFather token
DB_URL = os.getenv("DATABASE_URL", "sqlite:///./files.db")  # Postgres on Render
