import logging
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from sqlalchemy import Table, Column, Integer, String, MetaData, create_engine, insert, select
from sqlalchemy.exc import SQLAlchemyError
from config import BOT_TOKEN, DB_URL

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
engine = create_engine(DB_URL)
metadata = MetaData()

files = Table(
    "files", metadata,
    Column("id", Integer, primary_key=True),
    Column("file_id", String, nullable=False),
    Column("file_name", String, nullable=False),
)

metadata.create_all(engine)

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📂 Welcome! Send me a file and I’ll store it for you.")

async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.document:
        return

    file = update.message.document
    file_id = file.file_id
    file_name = file.file_name

    try:
        with engine.connect() as conn:
            conn.execute(insert(files).values(file_id=file_id, file_name=file_name))
            conn.commit()
        await update.message.reply_text(f"✅ Stored {file_name}\nUse /get {file_name} to download.")
    except SQLAlchemyError as e:
        logger.error(f"DB Error: {e}")
        await update.message.reply_text("⚠️ Failed to save file.")

async def get_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Usage: /get filename")
        return
    filename = " ".join(context.args)

    with engine.connect() as conn:
        query = select(files).where(files.c.file_name == filename)
        row = conn.execute(query).fetchone()

    if row:
        await update.message.reply_document(document=row.file_id)
    else:
        await update.message.reply_text("❌ File not found.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("get", get_file))
    app.add_handler(MessageHandler(filters.Document.ALL, save_file))
    app.run_polling()

if __name__ == "__main__":
    main()
