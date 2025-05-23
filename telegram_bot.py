import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from check_cert import check_cert
from concurrent.futures import ThreadPoolExecutor
import asyncio

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")

executor = ThreadPoolExecutor()


async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Checking the certificate...")

    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(executor, check_cert)

    await update.message.reply_text(result)


async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("check", check_command))

    webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"
    print(f"Webhook URL: {webhook_url}")

    await app.bot.set_webhook(webhook_url)

    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        webhook_url=webhook_url
    )


if __name__ == "__main__":
    asyncio.run(main())
