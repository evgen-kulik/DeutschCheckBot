import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from check_cert import check_cert
from concurrent.futures import ThreadPoolExecutor
import asyncio

# Загрузка переменных окружения
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")
PORT = int(os.getenv("PORT", 8080))

executor = ThreadPoolExecutor()


async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("📥 Получена команда /check")
    await update.message.reply_text("⏳ Checking the certificate...")
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(executor, check_cert)
    await update.message.reply_text(result)


async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("check", check_command))

    # Устанавливаем webhook
    webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"
    print(f"🌐 Установка webhook на: {webhook_url}")

    try:
        current = await app.bot.get_webhook_info()
        print(f"📡 Текущий webhook: {current.url}")
        if current.url != webhook_url:
            await app.bot.set_webhook(webhook_url)
            print("✅ Webhook установлен")
        else:
            print("ℹ️ Webhook уже установлен")
    except Exception as e:
        print(f"❌ Ошибка при установке webhook: {e}")

    await app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=webhook_url,
    )


if __name__ == "__main__":
    asyncio.run(main())
