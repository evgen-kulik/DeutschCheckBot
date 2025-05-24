import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from concurrent.futures import ThreadPoolExecutor
from check_cert import check_cert

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")
PORT = int(os.getenv("PORT", 8080))

executor = ThreadPoolExecutor()


async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("📥 Получена команда /check")
    await update.message.reply_text("⏳ Проверяю сертификат...")
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(executor, check_cert)
    await update.message.reply_text(result)


async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("check", check_command))

    webhook_url = f"{RENDER_EXTERNAL_URL}"  # без /webhook
    print(f"🌐 Установка webhook на: {webhook_url}")

    # Проверка и установка webhook
    info = await app.bot.get_webhook_info()
    print(f"📡 Текущий webhook: {info.url}")
    if info.url != webhook_url:
        await app.bot.set_webhook(webhook_url)
        print("✅ Webhook установлен")
    else:
        print("ℹ️ Webhook уже установлен")

    # Запуск сервера: PTB сам обрабатывает запросы на "/"
    await app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
    )

if __name__ == "__main__":
    asyncio.run(main())
