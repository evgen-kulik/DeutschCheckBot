import logging
import os
import asyncio
from aiohttp import web
import nest_asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from check_cert import check_cert
import subprocess

# Load environment variables from .env file
load_dotenv()
nest_asyncio.apply()

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load required environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8080))

if not TELEGRAM_BOT_TOKEN or not WEBHOOK_URL:
    raise ValueError("TELEGRAM_BOT_TOKEN and WEBHOOK_URL must be set in .env")

# Automatically install Playwright browsers if not already installed
if not os.path.exists("/opt/render/.cache/ms-playwright"):
    print("Installing Playwright browsers...")
    subprocess.run(["playwright", "install"], check=True)

# Dictionary to track certificate check tasks per user
user_tasks = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for the /start command. Sends a greeting message to the user.
    """
    await update.message.reply_text("👋 Hello! I'm DeutschCheckBot. Type /check to check the certificate.")


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for the /check command. Starts a new certificate check
    and cancels any previous task for this user if running.
    """
    chat_id = update.effective_chat.id

    if chat_id in user_tasks:
        task = user_tasks[chat_id]
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    await update.message.reply_text("⏳ Checking the certificate...")

    user_tasks[chat_id] = asyncio.create_task(run_check_and_send_result(update, context))


async def run_check_and_send_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Runs the certificate check and sends the result to the user.
    Handles cancellation and errors gracefully.

    Args:
        update (Update): Telegram update object.
        context (ContextTypes.DEFAULT_TYPE): Telegram context.
    """
    chat_id = update.effective_chat.id
    try:
        result = await check_cert()
        await context.bot.send_message(chat_id=chat_id, text=result)
    except asyncio.CancelledError:
        await context.bot.send_message(chat_id=chat_id, text="❌ Your previous check was cancelled.")
    except Exception:
        logger.exception("Error during certificate check")
        await context.bot.send_message(chat_id=chat_id, text="⚠️ An error occurred during certificate check.")
    finally:
        user_tasks.pop(chat_id, None)


async def clear_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for the /clear_tasks command. Cancels and clears all running user tasks.
    """
    for task in user_tasks.values():
        task.cancel()
    for task in user_tasks.values():
        try:
            await task
        except asyncio.CancelledError:
            pass
    user_tasks.clear()
    await update.message.reply_text("✅ All running tasks have been cleared.")


async def handle_webhook(request):
    """
    Handles incoming webhook requests from Telegram.

    Args:
        request (aiohttp.web.Request): Incoming HTTP request.

    Returns:
        web.Response: OK or error response.
    """
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.update_queue.put(update)
        return web.Response(text="OK")
    except Exception as e:
        logger.exception("Webhook error")
        return web.Response(status=500, text="Webhook error")


async def run():
    """
    Initializes and runs the Telegram bot using a webhook interface.
    """
    global application

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("check", check))
    application.add_handler(CommandHandler("clear_tasks", clear_tasks))

    await application.bot.delete_webhook(drop_pending_updates=True)
    await application.bot.set_webhook(url=WEBHOOK_URL)

    await application.initialize()
    await application.start()

    web_app = web.Application()
    web_app.router.add_post("/webhook/", handle_webhook)

    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    logger.info(f"Bot is running via webhook at {WEBHOOK_URL}")
    await asyncio.Event().wait()  # keeps running


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("Bot stopped manually.")
