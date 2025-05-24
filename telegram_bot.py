import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from check_cert import check_cert
from concurrent.futures import ThreadPoolExecutor

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")
PORT = int(os.getenv("PORT", 8080))

executor = ThreadPoolExecutor()


async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Checking the certificate...")
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(executor, check_cert)
    await update.message.reply_text(result)


async def start_bot():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("check", check_command))

    webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"
    print(f"Webhook URL: {webhook_url}")

    try:
        # Check if webhook already set to avoid flood control error
        current = await app.bot.get_webhook_info()
        if current.url != webhook_url:
            await app.bot.set_webhook(webhook_url)
    except Exception as e:
        print(f"⚠️ Failed to set webhook: {e}")

    await app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=webhook_url
    )


if __name__ == "__main__":
    asyncio.run(start_bot())
