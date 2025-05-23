import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from check_cert import check_cert

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")


async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Checking the certificate...")
    result = check_cert()
    await update.message.reply_text(result)


def main():
    app = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .webhook_path("/webhook")
        .build()
    )

    app.add_handler(CommandHandler("check", check_command))

    print(f"Webhook URL: https://{RENDER_EXTERNAL_URL}/webhook")

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        webhook_url=f"https://{RENDER_EXTERNAL_URL}/webhook"
    )


if __name__ == "__main__":
    main()
