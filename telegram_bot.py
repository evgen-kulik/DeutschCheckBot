import logging
import os
import asyncio
import nest_asyncio
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import Conflict
from check_cert import check_cert

load_dotenv()
nest_asyncio.apply()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables")

user_tasks = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("👋 Hello! I'm DeutschCheckBot. Type /check to check the certificate.")


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id

    # Cancel existing task for this chat if any
    if chat_id in user_tasks:
        task = user_tasks[chat_id]
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    await update.message.reply_text("⏳ Checking the certificate...")

    # Run new check task
    user_tasks[chat_id] = asyncio.create_task(run_check_and_send_result(update, context))


async def run_check_and_send_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    try:
        result = await check_cert()
        await context.bot.send_message(chat_id=chat_id, text=result)
    except asyncio.CancelledError:
        await context.bot.send_message(chat_id=chat_id, text="❌ Your previous check was cancelled.")
    except Exception as e:
        logger.exception("Error during certificate check")
        await context.bot.send_message(chat_id=chat_id, text="⚠️ An error occurred during certificate check.")
    finally:
        user_tasks.pop(chat_id, None)


async def clear_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    for task in user_tasks.values():
        task.cancel()
    for task in user_tasks.values():
        try:
            await task
        except asyncio.CancelledError:
            pass
    user_tasks.clear()
    await update.message.reply_text("✅ All running tasks have been cleared.")


async def run_bot():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("clear_tasks", clear_tasks))

    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
        await app.run_polling()
    except Conflict as conflict_error:
        logger.error("Bot conflict: another instance is already running. Terminate the other process or restart.")
        logger.debug(f"Conflict details: {conflict_error}")
    except Exception as e:
        logger.exception("Unexpected error during bot startup")


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_bot())
    except KeyboardInterrupt:
        logger.info("Bot stopped manually.")
